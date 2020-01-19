import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .models import WowmaItem, WowmaItemSearchResult
from .enums import *
import os

class WowmaApi:
    application_key = '28c3dd90e158d12967129fecf1010e5c63240714cd68683dcf66d44fc78f9dcc'
    shop_id = '44154399'
    endpoint = 'https://api.manager.wowma.jp/wmshopapi/'
    proxies = {
        'https': 'http://user:332191-Aa@stoneriver.info:8081'
    }
    
    def __init__(self):
        pass
    def _get_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {__class__.application_key}'
        }
    
    def search_item_info(self, limit, page, searchparams):
        offset = (page - 1) * limit
        parameters = {
            'shopId': __class__.shop_id,
            'totalCount': limit,
            'startCount': offset
        }
        if 'itemname' in searchparams:
            parameters['itemName'] = searchparams['itemname']
        if 'itemcode' in searchparams:
            parameters['itemCode'] = searchparams['itemcode']

        query_string = urlencode(parameters)
        url = f'{__class__.endpoint}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self._get_headers(), proxies = __class__.proxies)
        response_parsed = ET.fromstring(response.content)
        return WowmaItemSearchResult(response_parsed, limit, page)
        
wowma_api = WowmaApi()

