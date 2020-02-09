import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from wowma.models import *
from .enums import *
import os


class WowmaApi:
    proxies = {
        'https': 'http://user:332191-Aa@stoneriver.info:8081'
    }
    def __init__(self, auth_info):
        if not auth_info:
            raise Exception('Wowma認証情報が登録されていません')
        self.auth_info = auth_info
        self.valid = True
        self.error = None
    def get_headers(self, content_type):
        return {
            'Content-Type': content_type,
            'Authorization': f'Bearer {self.auth_info.application_key}'
        }

    def validate_response(self, response_parsed):
        self.valid = True
        self.error = None

        status = response_parsed.find('./result/status').text
        if status != API_STATUS_SUCCESS:
            self.valid = False
            self.error = f'[{response_parsed.find("./result/error/code").text}] {response_parsed.find("./result/error/message").text}'
        return self.valid

    # def fetch_shopcategories(self):
    #     parameters = {
    #         'shopId': self.auth_info.store_id
    #     }
    #     query_string = urlencode(parameters)
    #     url = f'{WOWMA_ENDPOINT}/searchShopCtgryInfos?{query_string}'
    #     response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
    #     response_parsed = ET.fromstring(response.content)
    #     if not self.validate_response(response_parsed):
    #         raise Exception(self.error)
    #     return response_parsed.findall('./shopCategoryInfo')
    
    def fetch_categories(self):
        url = f'{WOWMA_ENDPOINT}getCategoryTagInfo'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)

        return response_parsed.findall('./resultDetail/categoryInfo/ctgryList')
    def fetch_all(self):
        all_items = []
        offset = 0
        limit = 100
        while True:
            item_elements = self.search_item_info(offset, limit)
            
            all_items.extend(item_elements)
            if len(item_elements) < limit:
                break
            break
        
        return all_items

    def search_item_info(self, offset, limit, searchparams=None):
        parameters = {
            'shopId': self.auth_info.store_id,
            'totalCount': limit,
            'startCount': offset
        }
        # if 'itemname' in searchparams:
        #     parameters['itemName'] = searchparams['itemname']
        # if 'itemcode' in searchparams:
        #     parameters['itemCode'] = searchparams['itemcode']

        query_string = urlencode(parameters)
        url = f'{WOWMA_ENDPOINT}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        
        max_count = response_parsed.find('./searchResult/maxCount').text

        results = response_parsed.findall('./searchResult/resultItems')
        
        return results

    def add(self, request_element):
        url = f'{WOWMA_ENDPOINT}registerItemInfo/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=ET.tostring(request_element, encoding='utf-8'))
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        # add item object
        
    def update_item(self, item):
        url = f'{WOWMA_ENDPOINT}updateItemInfo/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.create_params(self.auth_info.store_id, mode = API_MODE_UPDATE))
        response_parsed = ET.fromstring(response.content)
        result_status = response_parsed.find('./result/status').text      
        if result_status == API_STATUS_ERROR:     
            error = response_parsed.find('./updateResult/error')
            error_code = error.find('./code').text
            error_message = error.find('./message').text
            item.valid = False
            item.error = f'{error_code}:{error_message}'
        else:
            # if success
            item.valid = True
        return item.valid

    def delete_item(self, id):
        item = Item.objects.get(id = id)
        item.delete()

        return
        url = f'{WOWMA_ENDPOINT}deleteItemInfos/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.create_params(self.auth_info.store_id, mode = API_MDOE_DELETE))
        response_parsed = ET.fromstring(response.content)
        result_status = response_parsed.find('./result/status').text      
        if result_status == API_STATUS_ERROR:     
            error = response_parsed.find('./deleteResult/error')
            error_code = error.find('./code').text
            error_message = error.find('./message').text
            item.valid = False
            item.error = f'{error_code}:{error_message}'
        else:
            # if success
            item.valid = True
        return item.valid
    
    def delete_shopcategory(self, shopcategory_id):
        url = f'{WOWMA_ENDPOINT}deleteShopCtgryInfo/'
        root = ET.Element('request')
        shopId = ET.SubElement(root, 'shopId')
        shopId.text = self.store_id
        shopcategory = ET.SubElement(root, 'shopCategoryId')
        shopcategory.text = shopcategory_id

        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data = ET.tostring(root))
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        return True