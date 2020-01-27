from django import forms
from .models import *
from .enums import *
import copy
        
import csv
from io import TextIOWrapper, StringIO

class AuthInfoModelForm(forms.ModelForm):
    class Meta:
        model = AuthInfo
        fields = ('application_key', 'store_id')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget = forms.TextInput(attrs={'class': 'form-control',})

class UploadedFileModelForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('item_csv', 'stock_csv')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget = forms.FileInput(attrs={'class': 'form-control',})
    
    def clean_item_csv(self):
        print('clean item csv called')
        item_csv = copy.deepcopy(self.cleaned_data['item_csv'])
        item_csv_data = csv.reader(TextIOWrapper(item_csv, encoding='cp932'))
        item_rows = list(item_csv_data)
        for line in item_rows:
            if len(line) != ItemCols.COLUMN_COUNT:
                raise forms.ValidationError(f"列数が不正です 期待:{ItemCols.COLUMN_COUNT}, 実態:{len(line)}")
        self.cleaned_data['item_count'] = len(item_rows) - 1
        return self.cleaned_data['item_csv']

    def clean_stock_csv(self):
        stock_csv = copy.deepcopy(self.cleaned_data['stock_csv'])
        stock_csv_data = csv.reader(TextIOWrapper(stock_csv, encoding='cp932'))
        for index, line in enumerate(stock_csv_data):
            if len(line) != StockCols.COLUMN_COUNT:
                raise forms.ValidationError(f"列数が不正です 期待:{StockCols.COLUMN_COUNT}, 実態:{len(line)}")
        return self.cleaned_data['stock_csv']
    
    def save(self, commit=True):
        instance = super(UploadedFileModelForm, self).save(commit=False)
        instance.item_count = self.cleaned_data['item_count']
        if commit:
            instance.save()
        return instance
