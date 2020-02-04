import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from .enums import *
import os


class WowmaApi:
    proxies = {
        'https': 'http://user:332191-Aa@stoneriver.info:8081'
    }
    def __init__(self, auth_info):
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

    def fetch_categories(self):
        parameters = {
            'shopId': self.auth_info.store_id
        }
        query_string = urlencode(parameters)
        url = f'{WOWMA_ENDPOINT}/searchShopCtgryInfos?{query_string}'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        return response_parsed.findall('./shopCategoryInfo')

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

        # query_string = urlencode(parameters)
        url = f'{WOWMA_ENDPOINT}searchItemInfos'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        
        max_count = response_parsed.find('./searchResult/maxCount').text
        return response_parsed.findall('./searchResult/resultItems')
    
    def add(self, request_element, categories, images):
        url = f'{WOWMA_ENDPOINT}registerItemInfo/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=ET.tostring(request_element, encoding='utf-8'))
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        item_element = request_element.find('./registerItem')
        item = Item(user = self.auth_info.user)
        item.set_attributes(item_element)

        register_stock_element = request_element.find('./registerStock')
        register_stock = RegisterStock(item = item)
        register_stock.set_attributes(register_stock_element)
    

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

    def delete_item(self, item):
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