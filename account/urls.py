from django.conf.urls import url
from .views import *
from . import views

urlpatterns = [
    url(r'^login/', login),
    # url(r'^leave/', leave),
    url(r'sign-up/$', views.UserCreate.as_view()),
    url(r'password_reset/$', views.ResetPassword.as_view()),
    url(r'password_change/$', views.ChangePassword.as_view()),
    url(r'follow/$', views.FollowSet.as_view()),
    url(r'profile-image_change/$', views.ProfileView.as_view()),
    url(r'^user-update/$', user_update),
    url(r'^myuser-get/(?P<pk>\d+)/$', myuser_get),
    url(r'^user-get/(?P<pk>\d+)/$', user_get),
    url(r'push/$', push_update),

]