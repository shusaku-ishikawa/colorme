from django.contrib import admin
from .models import Oauth

# Register your models here.
class OauthAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'client_secret_id', 'redirect_uri', 'authorization_code', 'access_token', 'access_token_expires_in', 'refresh_token')
admin.site.register(Oauth, OauthAdmin)
