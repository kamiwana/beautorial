from django.conf.urls import url
from .views import *

urlpatterns = [
  url(r'^$', ProductList.as_view(), name='product_list'),
]