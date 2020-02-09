from django import forms
from .models import *
from .enums import *
import copy    
import csv, xlrd
from io import TextIOWrapper, StringIO

class AuthInfoModelForm(forms.ModelForm):
    class Meta:
        model = AuthInfo
        fields = ('application_key', 'store_id')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget = forms.TextInput(attrs={'class': 'form-control',})
