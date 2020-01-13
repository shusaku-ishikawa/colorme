from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'wowma'

urlpatterns = [
    path('', views.DashBoard.as_view()),
]