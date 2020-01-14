import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .models import WowmaItem

API_STATUS_SUCCESS = '0'
API_STATUS_ERROR = '1'
            
class WowmaApi:
    application_key = '28c3dd90e158d12967129fecf1010e5c63240714cd68683dcf66d44fc78f9dcc'
    shop_id = '44154399'
    endpoint = 'https://api.manager.wowma.jp/wmshopapi/'
    def __init__(self):
        pass
    def _get_headers(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {__class__.application_key}'
        }
    
    def search_item_info(self, limit, offset):
        parameters = {
            'shopId': __class__.shop_id,
            'totalCount': limit,
            'startCount': offset
        }
        query_string = urlencode(parameters)
        url = f'{__class__.endpoint}searchItemInfos?{query_string}'
        response = requests.get(url, headers = self._get_headers())
        response_parsed = ET.fromstring(response.content)
        status = response_parsed.find('./result/status').text
        if status != API_STATUS_SUCCESS:
            # error
            error_code = response_parsed.find('./result/error/code').text
            error_message = response_parsed.find('./result/error/message').text
            raise Exception(f'{error_code} {error_message}')
        else:
            items = response_parsed.findall('./searchResult/resultItems')
            return [WowmaItem(item) for item in items]
           
wowma_api = WowmaApi()

