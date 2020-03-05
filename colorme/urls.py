from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'colorme'

urlpatterns = [
    path('dashboard', views.DashBoard.as_view(), name = 'dashboard'),
    path('jobs', views.Jobs.as_view(), name="job"),
    path('search', views.Search.as_view(), name = 'search'),
    path('operation', views.Operation.as_view(), name = 'operation'),
    path('upload', views.Upload.as_view(), name = 'upload'),
    path('process', views.process_uploaded_file, name = 'process'),   
]