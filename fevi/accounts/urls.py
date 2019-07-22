from django.urls import re_path
from rest_framework import routers
from accounts import views

router = routers.SimpleRouter()
router.register(r'account/users', views.AccountUsersViewSet, 'AccountUsers')

urlpatterns = router.urls + [
    re_path('^create-work-space/$', views.create_workspace, ),
    re_path('^signin/google/$', views.google_sign_in, )
]
