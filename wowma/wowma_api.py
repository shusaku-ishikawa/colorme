import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .models import WowmaItem, WowmaItemSearchResult
from .enums import *
          
class WowmaApi:
    application_key = '28c3dd90e158d12967129fecf1010e5c63240714cd68683dcf66d44fc78f9dcc'
    shop_id = '44154399'
    endpoint = 'https://api.manager.wowma.jp/wmshopapi/'
    limit = 10

    def __init__(self):
        pass
    def _get_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {__class__.application_key}'
        }
    
    def search_item_info(self, page):
        offset = (page - 1) * __class__.limit
        parameters = {
            'shopId': __class__.shop_id,
            'totalCount': __class__.limit,
            'startCount': offset
        }
        query_string = urlencode(parameters)
        url = f'{__class__.endpoint}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self._get_headers())
        response_parsed = ET.fromstring(response.content)
        return WowmaItemSearchResult(response_parsed, page)
        
wowma_api = WowmaApi()

