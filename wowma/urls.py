from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'wowma'

urlpatterns = [
    path('dashboard', views.DashBoard.as_view(), name = 'dashboard'),
]