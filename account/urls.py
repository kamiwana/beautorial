from django.conf.urls import url
from .views import *
from . import views

urlpatterns = [
    url(r'^login/', login),
    # url(r'^leave/', leave),
    url(r'sign-up/$', views.UserCreate.as_view()),
    url(r'password_reset/$', views.ResetPassword.as_view()),
    url(r'password_update/$',views.ChangePassword.as_view()),
    url(r'follow/$',views.FollowSet.as_view()),

]