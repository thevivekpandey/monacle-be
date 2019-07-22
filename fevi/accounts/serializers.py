from rest_framework.compat import unicode_to_repr
from rest_framework import serializers

from accounts.models import Account, Team, User


class CurrentTeamDefault(object):
    def set_context(self, serializer_field):
        self.team = serializer_field.context['request'].team

    def __call__(self):
        return self.team

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class AccountModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class TeamModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class CreateWorkSpaceSerializer(serializers.Serializer):
    workspace = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)
    gsuite_domain = serializers.CharField(max_length=100, required=False, source='gsuiteDomain')
    gsuite_domain_only = serializers.BooleanField(default=False, source='gsuiteDomainOnly')


class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField(max_length=30000)
    workspace = serializers.CharField(max_length=100)


class UserRoleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']
