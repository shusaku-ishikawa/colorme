import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .models import Item, ItemSearchResult
from .enums import *
import os


class WowmaApi:
    proxies = {
        'https': 'http://user:332191-Aa@stoneriver.info:8081'
    }
    def __init__(self, auth_info):
        self.application_key = auth_info.application_key
        self.store_id = auth_info.store_id

    def get_headers(self, content_type):
        return {
            'Content-Type': content_type,
            'Authorization': f'Bearer {self.application_key}'
        }
    
    def search_item_info(self, limit, page, searchparams):
        offset = (page - 1) * limit
        parameters = {
            'shopId': self.store_id,
            'totalCount': limit,
            'startCount': offset
        }
        if 'itemname' in searchparams:
            parameters['itemName'] = searchparams['itemname']
        if 'itemcode' in searchparams:
            parameters['itemCode'] = searchparams['itemcode']

        query_string = urlencode(parameters)
        url = f'{WOWMA_ENDPOINT}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        return ItemSearchResult(response_parsed, limit, page)

    def register_item(self, item):
        url = f'{WOWMA_ENDPOINT}registerItemInfo/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.create_params(self.store_id, mode = API_MODE_REGISTER))
        response_parsed = ET.fromstring(response.content)
        result_status = response_parsed.find('./result/status').text
        if result_status == API_STATUS_ERROR:     
            error = response_parsed.find('./registerResult/error')
            error_code = error.find('./code').text
            error_message = error.find('./message').text
            item.valid = False
            item.error = f'{error_code}:{error_message}'
        else:
            # if success
            item.valid = True
        print(ET.tostring(response_parsed, encoding='utf-8').decode())
        return item.valid

    def update_item(self, item):
        url = f'{WOWMA_ENDPOINT}updateItemInfo/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.create_params(self.store_id, mode = API_MODE_UPDATE))
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
        print(ET.tostring(response_parsed, encoding='utf-8').decode())
        return item.valid

    def delete_item(self, item):
        url = f'{WOWMA_ENDPOINT}deleteItemInfos/'
        print(item.create_params(self.store_id, mode = API_MDOE_DELETE))
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.create_params(self.store_id, mode = API_MDOE_DELETE))
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
        print(ET.tostring(response_parsed, encoding='utf-8').decode())
        return item.valid