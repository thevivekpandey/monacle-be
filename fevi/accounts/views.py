from django.shortcuts import render
from django.contrib.auth import get_user_model
from random import randint
import json
# Create your views here.

from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotFound, NotAcceptable
from rest_framework.authtoken.models import Token
from accounts.custom_permissions import IsSuperUser, IsAccountAdmin
from accounts.models import Account, User, AccountSettings, Team, DemoVisitor
from rest_framework.viewsets import ModelViewSet
from accounts.serializers import (
    CreateWorkSpaceSerializer,
    GoogleSignInSerializer,
    AccountModelSerializer,
    UserRoleModelSerializer,
    TeamModelSerializer
)

from accounts.third_party_signin.google_oauth import get_res_from_google


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsSuperUser,))  # IsAnalystAllowed
def create_workspace(request):
    data = request.data
    create_work_space_serializer = CreateWorkSpaceSerializer(data=data)
    if not create_work_space_serializer.is_valid():
        return Response(create_work_space_serializer.errors, status=400)
    workspace_identifier = data['workspace'].lower()
    workspace_exists = AccountSettings.objects.filter(workspace=workspace_identifier).exists()
    if workspace_exists:
        raise ValidationError('workspace: `' + workspace_identifier + '` [already exists, please choose another one]')
    email_exists = User.objects.filter(email=data['email']).exists()
    if email_exists:
        raise ValidationError('Email already exists, please choose another one')
    account = Account(name=data['name'])
    account.save()
    all_users_team = Team()
    all_users_team.name = 'AllUsers'
    all_users_team.account = account
    all_users_team.save()
    user = User()
    email_normalized = User.objects.normalize_email(data['email'])
    user.email = email_normalized
    user.username = email_normalized
    password = User.objects.make_random_password()
    user.set_password(password)
    user.account = account
    user.role = 'ANALYST'
    user.save()
    user.teams.add(all_users_team)
    user.save()
    account_settings = AccountSettings()
    account_settings.all_users_team = all_users_team
    account_settings.account = account
    account_settings.admin = user
    account_settings.workspace = workspace_identifier
    gsuite_domain_only = data['gsuiteDomainOnly']
    if gsuite_domain_only:
        account_settings.gsuite_domain_only = True
        account_settings.gsuite_domain = data['gsuiteDomain']
    account_settings.save()
    workspace_data = {
        'workspace': workspace_identifier,
        'username': email_normalized,
        'password': password
    }
    return Response(workspace_data)


@api_view(['POST'])
def google_sign_in(request):
    data = request.data
    gss = GoogleSignInSerializer(data=data)
    if not gss.is_valid():
        raise AuthenticationFailed(gss.errors)
    token = data['id_token']
    try:
        id_info = get_res_from_google(token)
    except Exception as e:
        raise AuthenticationFailed(str(e))
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise AuthenticationFailed('Wrong issuer.')
    account_settings = AccountSettings.objects.filter(workspace=data['workspace']).first()

    # Logging user in to demo workspace #
    if not account_settings:
        raise NotFound('Workspace not found')
    email = User.objects.normalize_email(id_info['email'])
    if account_settings.workspace == 'demo':
        email = User.objects.normalize_email(id_info['email'])
        demo_visitor = DemoVisitor(email=email)
        demo_visitor.save()
        count = account_settings.all_users_team.users.count()
        random_index = randint(0, count - 1)
        demo_user = account_settings.all_users_team.users.all()[random_index]
        t, created = Token.objects.get_or_create(user=demo_user)
        res = {
            'role': demo_user.role,
            'name': demo_user.first_name + ' ' + demo_user.last_name,
            'pictureUrl': demo_user.picture_url,
            'token': t.key,
            'default_team': TeamModelSerializer(account_settings.all_users_team).data,
            'account': AccountModelSerializer(account_settings.account).data,
            'isFirstTime': created
        }
        return Response(res)
    elif account_settings.workspace == 'fevi':
        if email not in settings.TEST_EMAILS:
            raise NotFound('UserNotFound')
        # if email == 'ravitejanandula@gmail.com':
        #     test_user = account_settings.all_users_team.users.filter(role='USER').first()
        # else:
        #     test_user = account_settings.all_users_team.users.filter(role='ANALYST').first()
        test_user = account_settings.all_users_team.users.filter(role='ANALYST').first()

        t, created = Token.objects.get_or_create(user=test_user)
        res = {
            'role': test_user.role,
            'pictureUrl': test_user.picture_url,
            'name': test_user.first_name + ' ' + test_user.last_name,
            'token': t.key,
            'default_team': TeamModelSerializer(account_settings.all_users_team).data,
            'account': AccountModelSerializer(account_settings.account).data,
            'isFirstTime': created
        }
        return Response(res)

    if (account_settings.gsuite_domain_only
            and 'hd' in id_info
            and id_info['hd'] != account_settings.gsuite_domain):
        raise NotAcceptable('Please use your company email address')

    u = User.objects.filter(email=email).first()
    name = id_info['given_name'] + ' ' + id_info['family_name']
    if not u:
        u = User()
        u.account = account_settings.account
        u.picture_url = id_info['picture']
        u.first_name = id_info['given_name']
        u.last_name = id_info['family_name']
        u.email = email
        u.username = email
        u.set_unusable_password()
        u.is_active = True
        u.save()
        u.teams.add(account_settings.all_users_team)
        u.save()
    t, created = Token.objects.get_or_create(user=u)
    token = t.key
    res = {
        'role': u.role,
        'pictureUrl': u.picture_url,
        'name': name,
        'token': token,
        'default_team': TeamModelSerializer(account_settings.all_users_team).data,
        'account': AccountModelSerializer(account_settings.account).data,
        'isFirstTime': created
    }
    return Response(res)


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsAccountAdmin,))  # IsAnalystAllowed
class AccountUsersViewSet(ModelViewSet):
    serializer_class = UserRoleModelSerializer

    def get_queryset(self):
        return self.request.account_settings.all_users_team.users.all()
