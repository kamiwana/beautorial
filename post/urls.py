from django.conf.urls import url
from .views import *

urlpatterns = [
  url(r'^step/$', StepViewSet.as_view({'get': 'list'})),
  url(r'^like/$', LikeSet.as_view()),
  url(r'^bookmark/$', BookmarkSet.as_view()),
  url(r'^follow-post-list/$', FollowPostList.as_view()),
  url(r'^like-post-list/$', LikePostList.as_view()),
  url(r'^bookmark-post-list/$', BookmarkPostList.as_view()),
  url(r'^explore/tags/(?P<tag>\w+)/$', PostViewSet.as_view({'get': 'list'})),
  url(r'^my-makeupcard-list/$', PostMyViewSet.as_view({'get': 'list'})),
  url(r'^$', PostViewSet.as_view({'get': 'list'})),
  url(r'^(?P<pk>\w+)/$', PostViewSet.as_view({'get': 'retrieve'}), name='post_detail'),

]