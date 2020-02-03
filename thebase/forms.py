from django import forms
from .models import *
from .enums import *
import copy,csv
from io import TextIOWrapper, StringIO
class OauthModelForm(forms.ModelForm):
    class Meta:
        model = Oauth
        fields = ('client_id', 'client_secret_id', 'redirect_uri')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget = forms.TextInput(attrs={'class': 'form-control',})