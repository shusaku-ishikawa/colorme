from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('login', views.Login.as_view(), name = 'login'),
    path('logout', views.Logout.as_view(), name = 'logout'),
    path('top', views.Top.as_view(), name = 'top'),
    
]