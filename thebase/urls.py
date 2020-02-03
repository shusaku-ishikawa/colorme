from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'thebase'

urlpatterns = [
    path('dashboard', views.DashBoard.as_view(), name = 'dashboard'),
    path('authorize', views.Authorize.as_view(), name = 'authorize'),
    path('search', views.Search.as_view(), name = 'search'),
    path('categories', views.Categories.as_view(), name = 'categories'),
    path('delete_categories', views.DeleteCategory.as_view(), name = 'delete_categories'),
    path('delete', views.Delete.as_view(), name = 'delete'),
]