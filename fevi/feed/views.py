from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication
)
from rest_framework.permissions import IsAuthenticated

from accounts.custom_permissions import IsPartOfTeam
from analyst.models import Question
from feed.custom_permissions import HasFeedCardPermission
from feed.serializers import (
    FeedCardModelSerializer,
    CommentModelSerializer,
    AdeptModelSerializer
)
from feed.models import FeedCard

d = [{
    "id": 4,
    "created": "2019-02-03T04:37:39.893123Z",
    "updated": "2019-02-03T04:37:39.893183Z",
    "team": 1,
    "question": 1,
    "data": {
        "header": [{"name": "name", "display": "Name", "axis": "X"},
                   {"name": "uv", "display": "UV", "axis": "Y"},
                   {"name": "pv", "display": "Light", "axis": "Y"},
                   {"name": "amt", "display": "Amount", "axis": "Y"}],
        "data": [{"name": "A", "uv": 300, "pv": 400, "amt": 3400}, {"name": "B", "uv": 400, "pv": 300, "amt": 6400},
                 {"name": "C", "uv": 300, "pv": 200, "amt": 2400}, {"name": "D", "uv": 200, "pv": 300, "amt": 2400},
                 {"name": "E", "uv": 278, "pv": 189, "amt": 2400}, {"name": "F", "uv": 189, "pv": 189, "amt": 2400},
                 {"name": "G", "uv": 189, "pv": 278, "amt": 2400}],
        "type": "LINE_CHART"}
}, {
    "id": 3,
    "created": "2019-02-03T04:37:39.893123Z",
    "updated": "2019-02-03T04:37:39.893183Z",
    "team": 1,
    "question": 1,
    "data": {
        "header": [{"name": "name", "display": "Name"}, {"name": "uv", "display": "UV"},
                   {"name": "pv", "display": "Light"}, {"name": "amt", "display": "Amount"}],
        "data": [{"name": "A", "uv": 300, "pv": 400, "amt": 3400},
                 {"name": "B", "uv": 400, "pv": 300, "amt": 6400},
                 {"name": "C", "uv": 300, "pv": 200, "amt": 2400},
                 {"name": "D", "uv": 200, "pv": 300, "amt": 2400},
                 {"name": "E", "uv": 278, "pv": 189, "amt": 2400},
                 {"name": "F", "uv": 189, "pv": 189, "amt": 2400},
                 {"name": "G", "uv": 189, "pv": 278, "amt": 2400}],
        "type": "TABLE"}
}, {
    "id": 2,
    "created": "2019-02-03T04:37:39.893123Z",
    "updated": "2019-02-03T04:37:39.893183Z",
    "team": 1,
    "question": 1,
    "data": {"data": {"text": "This is just a demo"}, "type": "TEXT"}
}, {
    "id": 1,
    "created": "2019-02-03T04:37:39.893123Z",
    "updated": "2019-02-03T04:37:39.893183Z",
    "team": 1,
    "question": 1,
    "data":
        {"data": {"text": "4738979"}, "type": "NUMBER"}
}]


@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def feed_v1(request):
    print(request.user)
    if request.method == 'GET':
        return Response(d)


@api_view(['GET', 'POST'])
def feed(request):
    """
    List all code snippets, or create a new snippet.
    """
    print(request.user)
    if request.method == 'GET':
        return Response(d)


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsPartOfTeam,))  # IsAnalystAllowed
class FeedModelViewSet(ReadOnlyModelViewSet):
    serializer_class = FeedCardModelSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('question',)
    ordering_fields = ('created',)
    ordering = ('-created',)

    def get_queryset(self):
        return self.request.team.feed_cards.all()


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsPartOfTeam, HasFeedCardPermission,))  # IsAnalystAllowed
class CommentModelViewSet(ModelViewSet):
    serializer_class = CommentModelSerializer

    def get_queryset(self):
        return self.request.feed_card.comments.all()


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsPartOfTeam, HasFeedCardPermission,))  # IsAnalystAllowed
class AdeptModelViewSet(ModelViewSet):
    serializer_class = AdeptModelSerializer

    def get_queryset(self):
        return self.request.feed_card.adepts.all()


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, ))  # IsAnalystAllowed
class UserFeed(ReadOnlyModelViewSet):
    serializer_class = FeedCardModelSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('question',)
    ordering_fields = ('created',)
    ordering = ('-created',)

    def get_queryset(self):
        qs = Question.objects.filter(team__in=self.request.user.teams.all()).values('id')
        fc_ids = []
        for q in qs:
            fc_id = FeedCard.objects.filter(question_id=q['id']).order_by('-created').values('id')[:1]
            if fc_id:
                fc_ids.append(fc_id[0]['id'])
        return FeedCard.objects.filter(id__in=fc_ids)
