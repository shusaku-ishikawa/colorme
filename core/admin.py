from django.contrib import admin
from core.models import User
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

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

admin.site.register(User, MyUserAdmin)