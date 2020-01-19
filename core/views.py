
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.views.generic import TemplateView

class Login(LoginView):
    """ログインページ"""
    template_name = 'login.html'
class Top(TemplateView):
    template_name = 'top.html'