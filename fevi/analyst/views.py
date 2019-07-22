# Create your views here.
from uuid import uuid1

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from analyst.custom_permissions import (
    HasPermissionForQuerying,
    IsAnalyst,
    HasTeamQuestionWritePermission
)
from accounts.custom_permissions import IsPartOfTeam

from analyst.serializers import (
    QuestionModelSerializer,
    DatSourceModelSerializer
)
from analyst.models import (
    DataSource,
    DBConfigurations
)
from analyst.tasks import (
    execute_query,
    get_sqlalchemy_engine_conn,
    execute_question,
    question_to_feed
)

from feed.serializers import FeedCardModelSerializer


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsAnalyst, IsPartOfTeam, HasPermissionForQuerying,))  # IsAnalystAllowed
def query(request, team, ds):
    if request.method == 'POST':
        data = request.data
        data_source = DataSource.objects.get(pk=ds, team=team)
        res, column_names = execute_query(data_source.uri, data['query'])
        data = {
            'response': res,
            'columns': column_names
        }
        return Response(data)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated, IsAnalyst, IsPartOfTeam, HasPermissionForQuerying,))  # IsAnalystAllowed
def on_demand(request, team, ds):
    if request.method == 'POST':
        data = request.data
        data['data_source'] = ds
        data['on_demand'] = True
        ser = QuestionModelSerializer(data=data, context={'request': request})
        if not ser.is_valid():
            return Response(ser.errors, status=400)
        else:
            q = ser.save()
            res_obj = question_to_feed(q, uuid1())
            feed_ser = FeedCardModelSerializer(instance=res_obj)
            return Response(feed_ser.data)


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes(
    (IsAuthenticated, IsAnalyst, IsPartOfTeam, HasTeamQuestionWritePermission,))  # IsAnalystAllowed
class QuestionViewSet(ModelViewSet):
    serializer_class = QuestionModelSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('publish', 'on_demand',)
    ordering_fields = ('created', 'updated')
    ordering = ('-updated', '-created',)

    def get_queryset(self):
        return self.request.team.questions.all()

    @action(detail=True, url_path='dry-run', url_name='dry-run', methods=['GET'])
    def dry_run(self, request, team, pk=None):
        try:
            question = request.team.questions.get(pk=pk)
            res, column_names = execute_question(question)
            data = {
                'query_response': res,
                'columns': column_names
            }
            return Response(data)
        except Exception as e:
            return Response(str(e))

    @action(detail=True, url_path='generate-feed-card', methods=['GET'])
    def generate_feed(self, request, team, pk=None):
        try:
            question = request.team.questions.get(pk=pk)
            res_obj = question_to_feed(question, uuid1())
            ser = FeedCardModelSerializer(instance=res_obj)
            return Response(data=ser.data)
        except Exception as e:
            return Response(data=str(e), status=400)


@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes(
    (IsAuthenticated, IsAnalyst, IsPartOfTeam,))  # IsAnalystAllowed
class DataSourceViewSet(ModelViewSet):
    serializer_class = DatSourceModelSerializer

    def get_queryset(self):
        return self.request.team.data_sources.all()

    @action(detail=False)
    def config(self, request, team):
        configs = DBConfigurations.TEMPLATES
        return Response(configs)

    @action(detail=False, methods=['post'])
    def connect(self, request, team):
        data = request.data
        try:
            uri = DBConfigurations.get_uri(data['conn_type'], data['conn_settings'])
            conn = get_sqlalchemy_engine_conn(uri)
            conn.close()
        except Exception as e:
            return Response(status=412, data=str(e))
        return Response()
