import requests
from urllib.parse import urlencode
from .enums import *
from .models import *

import os

class ThebaseApi:
        
    def __init__(self, oauth):
        if not oauth:
            raise Exception('BASE認証情報が登録されていません')
        self.oauth = oauth
    @property
    def api_header(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self.oauth.access_token}'
        }
    def search_items(self, q):
        if not self.oauthaccess_token_valid:
            self.oauthget_access_token(GRANT_TYPE_REFRESH_TOKEN)
        
        parameters = {
            'q': q,
            'limit': 100,
        }   
        query_string = urlencode(parameters)
        url = f'{THEBASE_ENDPOINT}1/items?{query_string}'
        response_json = requests.get(url, headers = self.api_header).json()
        print(response_json)
        if 'error' in response_json and response_json['error_description'] == 'アクセストークンが無効です。':
            self.oauthget_access_token(GRANT_TYPE_REFRESH_TOKEN)
            response_json = requests.get(url, headers = self.api_header).json()
        return ItemSearchResult(response_json, q)
    
    def fetch(self, offset, limit = 100, max_image_no = 10):
        self.oauth.refresh_if_necessary()
        params = {
            'offset': offset,
            'limit': limit,
            'max_image_no': max_image_no
        }
        query_string = urlencode(params)
        url = f'{THEBASE_ENDPOINT}/1/items?{query_string}'
        return requests.get(url, headers = self.api_header).json()
    def fetch_all(self):
        all_items = []
        offset = 0
        limit = 100
        while True:
            response_json = self.fetch(offset)
            if not self.validate_response(response_json):
                return False
            items = response_json['items']
            all_items.extend(items)
            offset += limit
            if len(items) < limit:
                return all_items
    def add_image(self, item, image_no, image_url):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/add_image'
        return requests.post(url, {'item_id':item.item_id,'image_no':image_no,'image_url':image_url}, headers = self.api_header).json()

    def delete_image(self, item, image_no):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/delete_image'
        return requests.post(url, {'item_id':item.item_id,'image_no':image_no}, headers = self.api_header).json()
    
    def delete_variation(self, item, variation_id):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/delete_variation'
        return requests.post(url, {'item_id':item.item_id,'variation_id':variation_id}, headers = self.api_header).json()
    
    def get_categories(self):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}/1/categories'
        return requests.get(url, headers = self.api_header).json()
    
    def add_category(self, category_name, parent_number):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}/1/categories/add'
        params = {
            'name': category_name,
        }
        if parent_number:
            params['parent_number'] = parent_number
        return requests.post(url, params, headers=self.api_header).json()
    def delete_category(self, category_id):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}/1/categories/delete'
        return requests.post(url, {'category_id': category_id}, headers=self.api_header).json()

    def get_item_categories(self, item):
        self.oauth.refresh_if_necessary()    
        url = f'{THEBASE_ENDPOINT}/1/item_categories/detail/{item.item_id}'
        return requests.get(url, headers = self.api_header).json()
        
    def add_item_category(self, item, category_id):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/item_categories/add'
        return requests.post(url, {'item_id':item.item_id, 'category_id': category_id}, headers = self.api_header).json()
        
    def delete_item_category(self, item, item_category_id):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/item_categories/delete'
        return requests.post(url, {'item_category_id':item_category_id}, headers = self.api_header).json()
    
    def validate_response(self, response_json):
        self.valid = True
        self.error = None
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

    def set_category_to_item(self, item, categories):
        category_1 = categories['category_1']
        category_2 = categories['category_2']
        if category_1:
            try:
                category_1_obj = Category.objects.get(name = category_1, parent_number = 0)
            except Category.DoesNotExist:
                # if category not found
                r = self.add_category(category_1, 0)
                if not self.validate_response(r):
                    raise Exception(f'カテゴリ追加時にエラー {self.error}')
                category_1_obj = Category(user = item.user)
                category_dict = [c for c in r['categories'] if c['name'] == category_1 and c['parent_number'] == 0][0]
                for k,v in category_dict.items():
                    setattr(category_1_obj, k, v)
                category_1_obj.save()
            else:
                pass
            
            if category_2:
                try:
                    category_2_obj = Category.objects.get(name = category_2, parent_number = category_1_obj.number)
                except Category.DoesNotExist:
                    # if new
                    r = self.add_category(category_2, category_1_obj.number)
                    if not self.validate_response(r):
                        raise Exception(f'カテゴリ追加時にエラー {self.error}')
                    category_2_obj = Category(user = item.user)
                    category_dict = [c for c in r['categories'] if c['name'] == category_1 and c['parent_number'] == category_1_obj.number][0]
                    for k,v in category_dict.items():
                        setattr(category_2_obj, k, v)
                    category_2_obj.save()
                else:
                    pass
            
            # add item category if none
            category_obj = category_2_obj if category_2 else category_1_obj

            try:
                item_category = ItemCategory.objects.get(item_id = item.item_id, category_id = category_obj.category_id)
            except ItemCategory.DoesNotExist:
                # if new
                r = self.add_item_category(item, category_obj.category_id)
                if not self.validate_response(r):
                    raise Exception(f'商品カテゴリ追加時にエラー {self.error}')
                item_category = [ic for ic in r['item_categories'] if ic['category_id'] == category_obj.category_id][0]
                item_category_obj = ItemCategory(user = item.user)
                for k,v in item_category.items():
                    setattr(item_category_obj, k, v)
                item_category_obj.save()
            else:
                pass
        return True      
    def set_images_to_item(self, item, images):
        # images
        for i, image_url in enumerate(images):
            #### image #####
            image_no = i + 1
            key = f'img{image_no}_origin'
            if getattr(item, key) == None or image_url != getattr(item, key): # if the registered image url changed or new image added
                print(f'No.{image_no} の画像を追加します {image_url}')
                image_response_json = self.add_image(item, image_no, image_url)
                self.validate_response(image_response_json)
                setattr(item, f'img{image_no}_origin', image_url)
            
    def add(self, item_params, categories, images):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/add'
        response_json = requests.post(url, data=item_params, headers = self.api_header).json()
        if not self.validate_response(response_json):
            raise Exception(self.error)

        item_json = response_json['item']
        item = Item()
        item.user = self.oauth.user
        variations = []
       
        item.set_attributes(item_json)
        # categories
        self.set_category_to_item(item, categories)
        # images
        self.set_images_to_item(item, images)

        return True

    def edit(self, item_params, categories, images ):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/edit'
        response_json = requests.post(url, data=item_params, headers = self.api_header).json()
        
        if not self.validate_response(response_json):
            raise Exception(self.error)
        else:
            item = Item.objects.get(item_id = item_params['item_id'])
            item_json = response_json['item']
            
            for key, value in item_json.items():
                if key == 'variations':
                    continue
                elif 'img' in key:
                    continue
                elif key in dir(item):
                    setattr(item, key, value)
            item.save()
            
            self.set_category_to_item(item, categories)
            self.set_images_to_item(item, images)

            for i in range(len(images) + 1, 11):
                # delete image
                r = self.delete_image(item, i)
                if not self.validate_response(r):
                    return False
                setattr(item, f'img{i}_origin', None)
            item.save()

            ### variation ###
            base_variations = item_json['variations']
            local_variations = item.variations.all()
            
            variation_response_json = None
            for bvar in base_variations:
                if bvar['variation_identifier'] not in [lvar.variation_identifier for lvar in local_variations if lvar.variation]:
                    print(f'バリエーション {bvar["variation"]} を削除します。')
                    variation_response_json = self.delete_variation(item, bvar['variation_id'])
                    self.validate_response(variation_response_json)

            
            variation_json = variation_response_json or response_json
            variation_json = variation_json['item']
            for var in variation_json['variations']:
                try:
                    variation_object = Variation.objects.get(variation_id = var['variation_id'])
                except Variation.DoesNotExist:
                    variation_object = Variation()
                    variation_object.item = item
                
                for key, value in var.items():
                    setattr(variation_object, key, value)
                variation_object.save()    
        
        return True
    def delete(self, item_id):
        self.oauth.refresh_if_necessary()
        url = f'{THEBASE_ENDPOINT}1/items/delete'
        response_json = requests.post(url, data={'item_id': item_id}, headers = self.api_header).json()
        if not self.validate_response(response_json):
            if self.error == '不正なitem_idです。':
                Item.objects.get(item_id = item_id).delete()
                return True
            else:
                raise Exception(self.error)
        Item.objects.get(item_id = item_id).delete()
        return True


