from django.db import models
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from thebase.models import Oauth as thebase_Oauth
from django.utils.translation import ugettext_lazy as _
from wowma.models import AuthInfo as wowma_Auth
from thebase.models import Oauth as thebase_Auth


class UserManager(BaseUserManager):
    """ユーザーマネージャー."""
    
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given email must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(usernaem, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    def __str__(self):
        return self.username
    username = models.CharField(_('username'), max_length = 100, primary_key = True)
    wowma_auth = models.OneToOneField(to = wowma_Auth, null = True, blank =True, on_delete = models.SET_NULL)
    thebase_auth = models.OneToOneField(to = thebase_Auth, null = True, blank = True, on_delete = models.SET_NULL)
    

    is_staff = models.BooleanField(
        _('管理者'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('利用開始'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
