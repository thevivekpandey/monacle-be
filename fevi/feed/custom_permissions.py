from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from feed.models import FeedCard


class HasFeedCardPermission(BasePermission):

    def has_permission(self, request, view):
        card_id = request.resolver_match.kwargs.get('feed_card')
        try:
            card = FeedCard.objects.filter(team=request.team, pk=card_id).first()
            if not card:
                raise NotFound('Card Not Found')
            else:
                request.feed_card = card
                return True
        # data source team should be present in analyst teams
        except FeedCard.DoesNotExist:
            raise NotFound('Team Not Found')
