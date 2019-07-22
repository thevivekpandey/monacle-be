from django.urls import path, re_path
from analyst import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'team/(?P<team>[0-9]+)/questions', views.QuestionViewSet, 'Questions')
router.register(r'team/(?P<team>[0-9]+)/data-sources', views.DataSourceViewSet, 'Question')

urlpatterns = [
                  re_path('^team/(?P<team>[0-9]+)/data-source/(?P<ds>[0-9]+)/query/$', views.query),
                  re_path('^team/(?P<team>[0-9]+)/data-source/(?P<ds>[0-9]+)/on-demand/$', views.on_demand)
              ] + router.urls
