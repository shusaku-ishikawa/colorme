from django.db import models
import requests
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
import datetime
from .enums import *
import os, json, csv

# Create your models here.
class Oauth(models.Model):
    def __str__(self):
        return self.client_secret_id or ''
    client_id = models.CharField(
        primary_key = True,
        max_length = 100
    )
    client_secret_id = models.CharField(
        max_length = 100,
    )
    redirect_uri = models.CharField(
        max_length = 100,
    )
    authorization_code = models.CharField(
        max_length = 100,
        null = True,
        blank = True,
    )
    access_token = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    access_token_expires_in = models.DateTimeField(
        null = True,
        blank = True
    )
    refresh_token = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    @property
    def access_token_valid(self):
        return self.access_token and timezone.now() < self.access_token_expires_in
    
    def authorize(self):
        path = '1/oauth/authorize'
        parameters = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read_items write_items',
        }
        url = f'{THEBASE_ENDPOINT}{path}?{urlencode(parameters)}'
        return requests.get(url).url
    def set_authorization_code(self, code):
        self.authorization_code = code
        self.save()
    
    def get_access_token(self, grant_type):
        path = '1/oauth/token'
        parameters = {
            'grant_type': grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret_id,
            'redirect_uri': self.redirect_uri
        }
        if grant_type == GRANT_TYPE_AUTHORIZATION_CODE:
            parameters['code'] = self.authorization_code
        elif grant_type == GRANT_TYPE_REFRESH_TOKEN:
            parameters['refresh_token'] = self.refresh_token
        
        url = f'{THEBASE_ENDPOINT}{path}'
        response_json = requests.post(url, parameters).json()
        if 'error' in response_json:
            raise Exception(f'{response_json["error"]}: {response_json["error_description"]}')
        else:
            self.access_token = response_json['access_token']
            self.access_token_expires_in = timezone.now() + datetime.timedelta(seconds=response_json['expires_in'])
            self.refresh_token = response_json['refresh_token']
            self.save()
    def refresh_if_necessary(self):
        if not self.access_token_valid:
            self.get_access_token(GRANT_TYPE_REFRESH_TOKEN)

class Item(models.Model):
    user = models.ForeignKey(to = 'core.User', on_delete = models.CASCADE)
    item_id = models.IntegerField(unique = True)
    title = models.CharField(max_length = 255,)
    category_id = models.IntegerField(null = True,blank = True)
    detail = models.TextField()
    price = models.IntegerField()
    proper_price = models.IntegerField(null = True, blank = True)
    item_tax_type = models.IntegerField()
    stock = models.IntegerField(null = True,blank = True)
    visible = models.IntegerField()
    list_order = models.IntegerField()
    identifier = models.CharField(max_length = 100,null = True)
    img1_origin = models.URLField(max_length = 255,null = True,blank = True)
    img2_origin = models.URLField(max_length = 255,null = True,blank = True)
    img3_origin = models.URLField(max_length = 255,null = True,blank = True)
    img4_origin = models.URLField(max_length = 255,null = True,blank = True)
    img5_origin = models.URLField(max_length = 255,null = True,blank = True)
    img6_origin = models.URLField(max_length = 255,null = True,blank = True)
    img7_origin = models.URLField(max_length = 255,null = True,blank = True)
    img8_origin = models.URLField(max_length = 255,null = True,blank = True)
    img9_origin = models.URLField(max_length = 255,null = True,blank = True)
    img10_origin = models.URLField(max_length = 255,null = True,blank = True)
    
    @property
    def categories(self):
        return self.category_id.split('/') if self.category_id else None

    @property
    def images(self):
        return [getattr(self, f'img{i}_origin') for i in range(1, 11) if getattr(self, f'img{i}_origin')]
    
    @property
    def visible_readable(self):
        if self.visible == 0:
            return '非公開'
        else:
            return '公開'
    @property
    def actual_stock(self):
        if len(self.variations) == 0:
            return self.stock
        else:
            stock = 0
            for v in self.variations.all():
                stock += v.variatoin_stock
            return stock
    @property
    def api_params(self):
        params = {
            'title': self.title,
            'detail': self.detail,
            'price': self.price,
            'item_tax_type': self.item_tax_type,
            'stock': self.actual_stock,
            'visible': self.visible,
            'identifier': self.identifier,
            'list_order': self.list_order,
        }
        for index, var in enumerate(self.variations):
            if var.variation_id:
                params[f'variation_id[{index}]'] = var.variation_id
            params[f'variation[{index}]'] = var.variation
            params[f'variation_stock[{index}]'] = var.variation_stock
            if var.variation_identifier:
                params[f'variation_identifier[{index}]'] = var.variation_identifier

        return params
    
    def set_attributes(self, item_dict):
        variations = []
        for key, value in item_dict.items():
            if key == 'variations':
                for index, var in enumerate(item_dict['variations']):
                    variation  = Variation()
                    for key, value in var.items():
                        setattr(variation, key, value)
                    variations.append(variation)
            elif key in dir(self):
                setattr(self, key, value)
        self.save()
        for var in variations:
            var.item = self
            var.save()
class Variation(models.Model):
    item = models.ForeignKey(to = Item,on_delete = models.CASCADE,related_name = 'variations')
    variation_id = models.IntegerField(null = True, blank = True)
    variation = models.CharField(max_length = 100)
    variation_stock = models.IntegerField()
    variation_identifier = models.CharField(max_length = 100, null = True, blank = True) 

class Category(models.Model):
    user = models.ForeignKey(to = 'core.User', on_delete = models.CASCADE)
    category_id = models.IntegerField(
        unique = True
    )
    name = models.CharField(
        max_length = 100,
    )
    list_order = models.IntegerField()
    number = models.IntegerField()
    parent_number = models.IntegerField(default = 0)
    code = models.CharField(max_length = 100)

class ItemCategory(models.Model):
    user = models.ForeignKey(to = 'core.User', on_delete = models.CASCADE)
    item_category_id = models.IntegerField(unique = True)
    item_id = models.IntegerField()
    category_id = models.IntegerField()

