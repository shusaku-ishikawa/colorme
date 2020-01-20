from django.db import models
import requests
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
import datetime
from .enums import *
import os, json

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

class Item(object):
    required_fields = [
        'title',
        'detail',
        'price',
        'item_tax_type',
        'stock',
        'visible',
        'list_order'
    ]
    def __init__(self, item_dict):
        if type(item_dict) == str: # if delete
            self.item_id = item_dict
        elif type(item_dict) == dict:
            self.item_id = item_dict['item_id']
            self.title = item_dict['title']
            self.detail = item_dict['detail']
            self.price = item_dict['price']
            self.proper_price = item_dict['proper_price'] if 'proper_price' in item_dict else None
            self.item_tax_type = item_dict['item_tax_type']
            self.stock = item_dict['stock']
            self.visible = item_dict['visible']
            self.list_order = item_dict['list_order']
            self.identifier = item_dict['identifier']
            for i in range(1, 20):
                setattr(self, f'img{i}_origin', item_dict[f'img{i}_origin'] if f'img{i}_origin' in item_dict else None)
            self.modified = item_dict['modified'] if 'modified' in item_dict else None
            
            self.variations = [self.Variation(variation_dict) for variation_dict in item_dict['variations']]
    class Variation(object):
        def __init__(self, variation_dict):
            self.variation_id = variation_dict['variation_id'] if 'variation_id' in variation_dict else None
            self.variation = variation_dict['variation']
            self.variation_stock = variation_dict['variation_stock']
            self.variation_identifier = variation_dict['variation_identifier'] if 'variation_identifier' in variation_dict else None
    @property
    def actual_stock(self):
        stock = 0
        for var in self.variations:
            stock += int(var.variation_stock)
        return stock
    @property
    def visible_readable(self):
        if self.visible == 0:
            return '非公開'
        else:
            return '公開'
    @property
    def add_params(self):
        params = {
            'title': self.title,
            'detail': self.detail,
            'price': self.price,
            'item_tax_type': self.item_tax_type,
            'stock': self.actual_stock if self.variations else self.stock,
            'visible': self.visible,
            'identifier': self.identifier,
            'list_order': self.list_order,
        }
        for index, var in enumerate(self.variations):
            params[f'variation[{index}]'] = var.variation
            params[f'variation_stock[{index}]'] = var.variation_stock
        return params
    def get_add_image_params(self, image_no, image_url):
        return {
            'item_id': self.item_id,
            'image_no': image_no,
            'image_url': image_url
        }

    def validate_for_add(self, line_number):
        self.line_number = line_number
        for f in __class__.required_fields:
            if not getattr(self, f) or getattr(self, f) == '':
                self.valid = False
                self.error = f'{f}は必須項目です'
                return False
        self.valid = True
        return True
    def get_header(self, access_token):
        return {
            'Authorization': f'Bearer {access_token}',
        }
    def add_image(self, oauth, image_no, image_url):
        if not oauth.access_token_valid:
            oauth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
        url = f'{THEBASE_ENDPOINT}1/items/add_image'
        return requests.post(url, self.get_add_image_params(image_no, image_url), headers = self.get_header(oauth.access_token)).json()

    def add(self, oauth):
        if not oauth.access_token_valid:
            oauth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
        url = f'{THEBASE_ENDPOINT}1/items/add'
        
        response_json = requests.post(url, data=self.add_params, headers = self.get_header(oauth.access_token)).json()
        
        if 'error' in response_json:
            if response_json['error_description'] == 'アクセストークンが無効です。':
                oauth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
                response_json = requests.post(url, self.add_params, headers = headers).json()
            if 'error' in response_json:
                self.valid = False
                self.error = response_json['error_description']
        else:
            item_json = response_json['item']
            self.item_id = item_json['item_id']
            for i in range(20):
                image_no = i + 1
                image_url = getattr(self, f'img{image_no}_origin')
                if not image_url or image_url == '':
                    break
                response_json = self.add_image(oauth, image_no, image_url)
                if 'error' in response_json:
                    self.valid = False
                    self.error = response_json['error_description']
                    break
        return self.valid

    def edit(self):
        pass
    def delete(self, oauth):
        if not self.item_id:
            self.valid = False
            self.error = 'item idがセットされていません'
            return
        url = f'{THEBASE_ENDPOINT}1/items/delete'
        response_json = requests.post(url, data={'item_id': self.item_id}, headers = self.get_header(oauth.access_token)).json()
        if 'error' in response_json:
            self.valid = False
            self.error = response_json['error_description']
        elif 'result' in response_json and response_json['result']:
            self.valid = True
        return self.valid

        
class ItemSearchResult(object):
    def __init__(self, response_dict, q):
        if 'error' in response_dict:
            self.error = self.Error(response_dict)      
        else:
            items = response_dict['items']
            self.q = q
            self.items = [Item(item) for item in items]
            
    class Error(object):
        def __init__(self, error_dict):
            self.code = error_dict['error']
            self.description = error_dict['error_description']

class UploadFileColumns(object):
    item_id = 0
    identifier = 1
    category_id = 2
    title = 3
    price = 4
    item_tax_type = 5
    detail = 6
    variation_start = 7
    stock = 27
    list_order = 28
    visible = 29
    delivery_company_id = 30
    img_origin_start = 31
    variation_stock_start = 51
