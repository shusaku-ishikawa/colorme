from django import forms
from .models import *
from .enums import *
import csv, os
from io import TextIOWrapper, StringIO
from django.core.files.storage import default_storage
from django.conf import settings

class UploadFileModelForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ('user', 'file_type', 'csv_file',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['csv_file'].widget.attrs['class'] = 'form-control'
        self.fields['file_type'].widget.attrs['class'] = 'form-control'
    def save(self, commit=True):
        instance = super(UploadFileModelForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance
