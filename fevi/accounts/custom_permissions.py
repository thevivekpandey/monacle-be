from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from accounts.models import Team, AccountSettings


class IsSuperUser(BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAccountAdmin(BasePermission):

    def has_permission(self, request, view):
        try:
            account_settings = AccountSettings.objects.filter(admin=request.user).first()
            if not account_settings:
                raise NotFound('Account Settings not found')
            else:
                request.account_settings = account_settings
                return True
        # data source team should be present in analyst teams
        except AccountSettings.DoesNotExist:
            raise NotFound('Team Not Found')


class IsPartOfTeam(BasePermission):

    def has_permission(self, request, view):
        team_id = request.resolver_match.kwargs.get('team')
        try:
            team = request.user.teams.filter(pk=team_id).first()
            if not team:
                raise NotFound('Team Not Found')
            else:
                request.team = team
                return True
        # data source team should be present in analyst teams
        except Team.DoesNotExist:
            raise NotFound('Team Not Found')
