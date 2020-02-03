from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'wowma'

urlpatterns = [
    path('dashboard', views.DashBoard.as_view(), name = 'dashboard'),
    path('search', views.Search.as_view(), name = 'search'),
    path('delete', views.Delete.as_view(), name = 'delete'),
]