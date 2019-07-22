from django.urls import re_path
from rest_framework import routers
from feed import views

router = routers.SimpleRouter()
router.register(r'team/(?P<team>[0-9]+)/feed-cards/(?P<feed_card>[0-9]+)/comments', views.CommentModelViewSet,
                'Comment')
router.register(r'team/(?P<team>[0-9]+)/feed-cards/(?P<feed_card>[0-9]+)/adepts', views.AdeptModelViewSet, 'Adept')
router.register(r'team/(?P<team>[0-9]+)/feed-cards', views.FeedModelViewSet, 'Feed')
router.register(r'user', views.UserFeed, 'UserFeed')

urlpatterns = router.urls + [
    re_path('^feed/$', views.feed),
    re_path('^feed/v1/$', views.feed_v1)
]
