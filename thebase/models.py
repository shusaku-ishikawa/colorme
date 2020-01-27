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

class UploadedFile(models.Model):
    item_csv = models.FileField(
        verbose_name = 'item csv',
        upload_to = 'item_csv'
    )
    item_count = models.IntegerField(
        verbose_name = '登録商品数'
    )
    uploaded_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    processed_at = models.DateTimeField(
        verbose_name = '処理日',
        null = True,
        blank = True
    )
    def dictize_params(self, cols):
        ret = {}
        ret['item_id'] = cols[ItemCols.item_id]
        ret['identifier'] = cols[ItemCols.identifier]
        ret['category_id'] = cols[ItemCols.category_id].splitlines()
        ret['title'] = cols[ItemCols.title]
        ret['price'] = cols[ItemCols.price]
        ret['item_tax_type'] = cols[ItemCols.item_tax_type]
        ret['detail'] = cols[ItemCols.detail]
        ret['variations'] = [{'variation_id': cols[ItemCols.variation_start + 2*i], 'variation': cols[ItemCols.variation_start + 2*i + 1], 'variation_stock': cols[ItemCols.variation_stock_start + i]} for i in range(20) if cols[ItemCols.variation_start + 2*i + 1] != '']
        for i in range(20):
            if not cols[ItemCols.img_origin_start + i] or cols[ItemCols.img_origin_start + i] == '':
                break
            key = f'img{i + 1}_origin'
            ret[key] = cols[ItemCols.img_origin_start + i]
        ret['stock'] = cols[ItemCols.stock]
        ret['list_order'] = cols[ItemCols.list_order]
        ret['visible'] = cols[ItemCols.visible]
        ret['delivery_company_id'] = cols[ItemCols.delivery_company_id]
        return ret

    def get_item_objects(self):
        items_to_register = []
        with open(self.item_csv.path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for index, line in enumerate(reader):
                if index == 0:
                    continue
                param_dict = self.dictize_params(line)
                item = Item(param_dict)
                if not item.validate_for_add(index):
                    all_ok = False
                items_to_register.append(item)
        return items_to_register
class UploadFileErrorRecord(models.Model):
    parent_file = models.ForeignKey(
        verbose_name = '親ファイル',
        to = UploadedFile,
        on_delete = models.CASCADE
    )
    timing = models.CharField(
        verbose_name = 'エラータイミング',
        max_length = 100
    )
    line_number = models.IntegerField(
        verbose_name = '行番号',
    )
    error_message = models.CharField(
        verbose_name = 'エラー',
        null = True,
        blank = True,
        max_length = 255
    )

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
            self.category_id = item_dict['category_id'] if 'category_id'  in item_dict else None
            self.detail = item_dict['detail']
            self.price = item_dict['price']
            self.proper_price = item_dict['proper_price'] if 'proper_price' in item_dict else None
            self.item_tax_type = item_dict['item_tax_type']
            self.stock = item_dict['stock']
            self.visible = item_dict['visible']
            self.list_order = item_dict['list_order']
            self.identifier = item_dict['identifier']
            for i in range(20):
                image_no = i + 1
                setattr(self, f'img{image_no}_origin', item_dict[f'img{image_no}_origin'] if f'img{image_no}_origin' in item_dict else None)
            self.modified = item_dict['modified'] if 'modified' in item_dict else None
            
            self.variations = [self.Variation(variation_dict) for variation_dict in item_dict['variations']]
    class Variation(object):
        def __init__(self, variation_dict):
            self.variation_id = variation_dict['variation_id'] if 'variation_id' in variation_dict else None
            self.variation = variation_dict['variation']
            self.variation_stock = variation_dict['variation_stock']
            self.variation_identifier = variation_dict['variation_identifier'] if 'variation_identifier' in variation_dict else None
    @property
    def images(self):
        return [(f'img{i+1}_origin', getattr(self, f'img{i+1}_origin')) for i in range(20) if getattr(self, f'img{i+1}_origin')]
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
    @property
    def edit_params(self):
        params = {
            'item_id': self.item_id,
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
            if var.variation and var.variation != '':
                params[f'variation_id[{index}]'] = var.variation_id or ''
                params[f'variation[{index}]'] = var.variation
                params[f'variation_stock[{index}]'] = var.variation_stock
        return params
    
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
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/add_image'
        return requests.post(url, {'item_id':self.item_id,'image_no':image_no,'image_url':image_url}, headers = self.get_header(oauth.access_token)).json()

    def delete_image(self, oauth, image_no):
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/delete_image'
        return requests.post(url, {'item_id':self.item_id,'image_no':image_no}, headers = self.get_header(oauth.access_token)).json()
    
    def delete_variation(self, oauth, variation_id):
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/delete_variation'
        return requests.post(url, {'item_id':self.item_id,'variation_id':variation_id}, headers = self.get_header(oauth.access_token)).json()
    
    def get_item_categories(self, oauth):
        oauth.refresh_if_necessary()    
        url = f'{THEBASE_ENDPOINT}/1/item_categories/detail/{self.item_id}'
        return requests.get(url, headers = self.get_header(oauth.access_token)).json()
        
    def add_item_category(self, oauth, item_category_id):
        print('add item category')
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/item_categories/add'
        return requests.post(url, {'item_id':self.item_id, 'category_id': item_category_id}, headers = self.get_header(oauth.access_token)).json()
        
    def delete_item_category(self, oauth, item_category_id):
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/item_categories/delete'
        return requests.post(url, {'item_category_id':item_category_id}, headers = self.get_header(oauth.access_token)).json()
    
    def validate_response(self, response_json):
        if 'error' in response_json:
            self.valid = False
            self.error = response_json['error_description']
            return False
        elif 'name' in response_json:
            self.valid = False
            self.error = response_json['message']
            return False
        else:
            return True
    def add(self, oauth):
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/add'
        
        response_json = requests.post(url, data=self.add_params, headers = self.get_header(oauth.access_token)).json()
        
        if not self.validate_response(response_json):
            return False
        else:
            item_json = response_json['item']
            self.item_id = item_json['item_id']
            # categories
            for category_id in self.category_id:
                category_respnose = self.add_item_category(oauth, category_id)
                if not self.validate_response(category_respnose):
                    return False
        
            # images
            for i in range(20):
                image_no = i + 1
                image_url = getattr(self, f'img{image_no}_origin')
                if not image_url:
                    break
                response_json = self.add_image(oauth, image_no, image_url)
                self.validate_response(response_json)
        return self.valid
    
    def edit(self, oauth):
        oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/edit'
        response_json = requests.post(url, data=self.edit_params, headers = self.get_header(oauth.access_token)).json()
        
        if not self.validate_response(response_json):
            return False
        else:
            item_json = response_json['item']
            self.item_id = item_json['item_id']
            
            # get current categories
            item_category_json = self.get_item_categories(oauth)
            if not self.validate_response(item_category_json):
                return False
            item_categories = [str(ic['category_id']) for ic in item_category_json['item_categories']]
            print(f'current category {item_categories}' )

            new_categories = list(set(self.category_id) - set(item_categories))
            old_categories = list(set(item_categories) - set(self.category_id))
            # set category
            for new_ic in new_categories:
                if not self.validate_response(self.add_item_category(oauth, new_ic)):
                    return False
            for old_ic in old_categories:
                old_item_category_id = [ic["item_category_id"] for ic in item_category_json if ic['item_category'] == old_ic][0]
                if not self.validate_response(self.delete_item_category(oauth, old_item_category_id)):
                    return False

            # add images if changed
            for i in range(20):
                #### image #####
                image_no = i + 1
                key = f'img{image_no}_origin'
                image_url = getattr(self, key)
                if image_url and ((key in item_json and item_json[key] != image_url) or (key not in item_json and image_url)): # if the registered image url changed or new image added
                    print(f'adding_image {image_no}')
                    print(f'{image_no} {image_url}')
                    image_response_json = self.add_image(oauth, image_no, image_url)
                    self.validate_response(image_response_json)

                elif key in item_json and item_json[key] and not image_url: # if image deleted
                    print(f'deleting image{image_no}')
                    image_response_json = self.delete_image(oauth, image_no)
                    self.validate_response(image_response_json)
                else:
                    pass

            ### variation ###
            base_variations = item_json['variations']
            local_variations = self.variations
            for bvar in base_variations:
                if bvar['variation'] not in [lvar.variation for lvar in local_variations if lvar.variation]:
                    print(f'deleting variation {bvar["variation_id"]}')
                    variation_response_json = self.delete_variation(oauth, bvar['variation_id'])
                    self.validate_response(variation_response_json)
                
        return self.valid
    def delete(self, oauth):
        oauth.refresh_if_necessary()
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

