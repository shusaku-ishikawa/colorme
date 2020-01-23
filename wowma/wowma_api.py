import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .models import Item, ItemSearchResult
from .enums import *
import os
from dicttoxml import dicttoxml


class WowmaApi:
    proxies = {
        'https': 'http://user:332191-Aa@stoneriver.info:8081'
    }
    
    def __init__(self, auth_info):
        self.application_key = auth_info.application_key
        self.store_id = auth_info.store_id

    def get_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
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
        response = requests.get(url, headers = self.get_headers(), proxies = __class__.proxies)
        #print(response.content)
        response_parsed = ET.fromstring(response.content)
        return ItemSearchResult(response_parsed, limit, page)
    
