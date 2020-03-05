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
            error_elem = response_parsed.find('.//error')

            self.error = f'[{error_elem.find("./code").text}] {error_elem.find("./message").text}'
        return self.valid

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
        query_string = urlencode(parameters)
        url = f'{WOWMA_ENDPOINT}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self.get_headers('application/x-www-form-urlencoded'), proxies = self.proxies)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        
        max_count = response_parsed.find('./searchResult/maxCount').text

        results = response_parsed.findall('./searchResult/resultItems')
        
        return results
    
    def add_or_edit(self, colorme_item):
        try:
            wowma_item = Item.objects.get(itemManagementId = colorme_item.kataban)
        except Item.DoesNotExist:
            # if new
            mode = API_MODE_REGISTER
            lotNumber = None
        else:
            mode = API_MODE_UPDATE
            lotNumber = wowma_item.lotNumber

        url = f'{WOWMA_ENDPOINT}{mode}ItemInfo/'
        params = colorme_item.wowma_api_params(self.auth_info.store_id, mode, lotNumber = lotNumber)
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data = params)
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        
        if mode == API_MODE_REGISTER:
            item = Item(user = self.auth_info.user)
            register_item = colorme_item.xml_serialize_item(mode = API_MODE_REGISTER)
            register_stock = colorme_item.xml_serialize_stock(mode = API_MODE_REGISTER)
            register_item.append(register_stock)
            item.set_attributes(register_item)

        return True

    def delete(self, id):
        item = Item.objects.get(id = id)
        url = f'{WOWMA_ENDPOINT}deleteItemInfos/'
        response = requests.post(url, headers = self.get_headers('application/xml; charset=utf-8'), proxies = self.proxies, data=item.delete_request_param(self.auth_info.store_id))
        response_parsed = ET.fromstring(response.content)
        if not self.validate_response(response_parsed):
            raise Exception(self.error)
        item.delete()
        return True
