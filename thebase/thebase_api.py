import requests
from urllib.parse import urlencode
from .enums import *
from .models import *

import os

class ThebaseApi:
        
    def __init__(self):
        pass
    def get_headers(self, access_token):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {access_token}'
        }
    def search_items(self, oauth, q):
        if not oauth.access_token_valid:
            oauth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
        
        parameters = {
            'q': q,
            'limit': 100,
        }   
        query_string = urlencode(parameters)
        url = f'{THEBASE_ENDPOINT}1/items?{query_string}'
        response_json = requests.get(url, headers = self.get_headers(oauth.access_token)).json()
        if 'error' in response_json and response_json['error_description'] == 'アクセストークンが無効です。':
            oauth.get_access_token(GRANT_TYPE_REFRESH_TOKEN)
            response_json = requests.get(url, headers = self.get_headers(oauth.access_token)).json()
        
        return ItemSearchResult(response_json, q)
        
thebase_api = ThebaseApi()

