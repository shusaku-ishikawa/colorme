from django.contrib import admin
from core.models import User
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from wowma.models import *

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'wowma_auth', 'thebase_auth')

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('wowma_auth', 'thebase_auth')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'wowma_auth', 'thebase_auth', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('username', 'wowma_auth', 'thebase_auth', 'is_staff', 'is_active', 'is_superuser')

class WowmaItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Item._meta.fields if field.name != "id"]
class WowmaRegisterStockAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RegisterStock._meta.fields if field.name != "id"]
class WowmaChoicesStockAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChoicesStock._meta.fields if field.name != "id"]
class WowmaShopCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShopCategory._meta.fields if field.name != "id"]

admin.site.register(User, MyUserAdmin)
admin.site.register(Item, WowmaItemAdmin)
admin.site.register(RegisterStock, WowmaRegisterStockAdmin)
admin.site.register(ChoicesStock, WowmaChoicesStockAdmin)
admin.site.register(ShopCategory, WowmaShopCategoryAdmin)
