from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'thebase'

urlpatterns = [
    path('dashboard', views.DashBoard.as_view(), name = 'dashboard'),
    path('authorize', views.Authorize.as_view(), name = 'authorize'),
    path('search', views.Search.as_view(), name = 'search'),
    path('delete', views.Delete.as_view(), name = 'delete'),
    path('upload', views.Upload.as_view(), name = 'upload'),

]