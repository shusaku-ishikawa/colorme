from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AuthInfo

# Register your models here.
class AuthInfoAdmin(admin.ModelAdmin):
    list_display = ('application_key', 'store_id')
admin.site.register(AuthInfo, AuthInfoAdmin)
