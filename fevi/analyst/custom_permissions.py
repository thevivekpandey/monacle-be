from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound
from accounts.models import User
from analyst.models import DataSource, Team
import logging

logger = logging.getLogger(__name__)


class IsAnalyst(BasePermission):

    def has_permission(self, request, view):
        logger.debug(request.user.role == User.ANALYST)
        return request.user.role == User.ANALYST


class HasPermissionForQuerying(BasePermission):

    def has_permission(self, request, view):
        ds = request.resolver_match.kwargs.get('ds')
        team_id = request.resolver_match.kwargs.get('team')

        try:
            data_source_exists = DataSource.objects.filter(pk=ds, team=team_id).exists()
            if data_source_exists:
                return True
            else:
                raise NotFound('DataSource Not Found')
        # data source team should be present in analyst teams
        except DataSource.DoesNotExist:
            raise NotFound('DataSource Not found')
        except Team.DoesNotExist:
            raise NotFound('Team Not found')


class HasTeamQuestionWritePermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        try:
            if 'data_source' not in request.data:
                raise NotFound('DataSource Not found')
            ds_exists = request.team.data_sources.filter(pk=request.data['data_source']).exists()
            if ds_exists:
                return True
            raise NotFound('DataSource Not found')
        # data source team should be present in analyst teams
        except Team.DoesNotExist:
            raise NotFound('Team Not Found')
        except DataSource.DoesNotExist:
            raise NotFound('DataSource Not found')


