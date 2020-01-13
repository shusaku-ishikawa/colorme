import requests
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

API_STATUS_SUCCESS = '0'
API_STATUS_ERROR = '1'


class WowmaItemModel:   
    def __init__(self, item_element):
        self.lot_number = item_element.find('lotNumber')
        self.item_name = item_element.find('itemName')
        self.item_management_id = item_element.find('itemManagementId')
        self.item_management_name = item_element.find('itemManagementName')
        self.item_code = item_element.find('itemCode')
        self.item_price = item_element.find('itemPrice')
        self.sell_method_segment = item_element.find('sellMethodSegment')
        self.release_date = item_element.find('releaseDate')
        self.reserve_regst_date = item_element.find('reserveRegstDate')
        self.tas_segment = item_element.find('taxSegment')
        self.postage_segment = item_element.find('postageSegment')
        self.postage = item_element.find('postage')
        self.deliverys = [self.Delivery(delivery) for delivery in item_element.findall('deliverys')]
        self.delivery_method = [self.DeliveryMethod(delivery_method) for delivery_method in item_element.findall('deliveryMethod')]
        self.public_start_date = item_element.find('publicStartDate')
        self.gift_packing_segment = item_element.find('giftPackingSegment')
        self.noshi_segment = item_element.find('noshiSegment')
        self.limited_order_segment = item_element.find('limitedOrderSegment')
        self.limited_order_count = item_element.find('limitedOrderCount')
        self.description = item_element.find('description')
        self.description_for_sp = item_element.find('descriptionForSP')
        self.description_for_pc = item_element.find('descriptionForPC')
        self.detail_title = item_element.find('detailTitle')
        self.detail_description = item_element.find('detailDescription')
        self.specs = [self.Spec(spec) for spec in item_element.findall('specs')]
        self.search_keywords = [self.SearchKeyword(search_keyword) for search_keyword in item_element.findall('searchKeywords')]
        self.images = [self.Image(image) for image in item_element.findall('images')]
        self.category_id = item_element.find('ctgryId')
        self.category_name = item_element.find('ctgryName')
        self.tags = [self.Tag(tag) for tag in item_element.findall('tags')]
        self.shop_categorys = [self.ShopCategory(shop_category) for shop_category in item_element.findall('shopCategory')]
        self.jan = item_element.find('jan')
        self.isbn = item_element.find('isbn')
        self.item_model = item_element.find('itemModel')
        self.limited_password = item_element.find('limitedPasswd')
        self.limiete_password_page_title = item_element.find('limitedPasswdPageTitle')
        self.limited_password_page_messsage = item_element.find('limitedPasswdPageMessage')
        self.sale_status = item_element.find('saleStatus')
        self.item_options = [self.ItemOption(item_option) for item_option in item_element.findall('itemOptions')]
        self.item_option_commissions = [self.ItemOptionCommission(item_option_commission) for item_option_commission in item_element.findall('itemOptionCommissions')]
        self.point_rate = item_element.find('pointRate')
        self.favorite_count = item_element.find('favoriteCount')
        self.receipt_request_count = item_element.find('receiptRequestCount')
        self.stock_request_config = item_element.find('stockRequestConfig')
        self.stock_request_count = item_element.find('stockRequestCount')
        self.register_stocks = [self.RegisterStock(register_stock) for register_stock in item_element.findall('registerStock')]

    class Delivery:
        def __init__(self, delivery_element):
            self.delivery_id = delivery_element.find('deliveryId')
            self.delivery_seq = delivery_element.find('deliverySeq')
    class DeliveryMethod:
        def __init__(self, delivery_method_element):
            self.delivery_method_id = delivery_method_element.find('deliveryMethodId')
            self.delivery_method_seq = delivery_method_element.find('deliveryMethodSeq')
            self.delivery_method_name = delivery_method_element.find('deliveryMethodName')
    class Spec:
        def __init__(self, spec_element):
            self.spec_title = spec_element.find('specTitle')
            self.detail_specs = [self.DetailSpec(detail_spec) for detail_spec in spec_element.findall('detailSpecs')]
        class DetailSpec:
            def __init__(self, detail_spec):
                self.spec_name = detail_spec.find('specName')
                self.spec = detail_spec.find('spec')
                self.spec_seq = detail_spec.find('specSeq')
    class SearchKeyword:
        def __init___(self, search_keyword_element):
            self.search_keyword = search_keyword_element.find('saerchKeyword')
            self.search_keyword_seq = search_keyword_element.find('searchKeywordSeq')
    class Image:
        def __init__(self, item_element):
            self.image_url = item_element.find('imageUrl')
            self.image_name = item_element.find('imageName')
            self.imange_seq = item_element.find('imageSeq')
    class Tag:
        def __init__(self, tag_element):
            self.tag_id = tag_element.find('tagId')
    class ShopCategory:
        def __init__(self, shop_category_element):
            self.shop_category_name = shop_category_element.find('shopCategoryName')
            self.shop_category_disp_seq = shop_category_element.find('shopCategoryDispSeq')
    class ItemOption:
        def __init__(self, item_option_element):
            self.item_option_title = item_option_element.find('itemOptionTitle')
            self.item_option = item_option_element.find('itemOption')
            self.item_option_seq = item_option_element.find('itemOptionSeq')
    class ItemOptionCommission:
        def __init__(self, item_option_element):
            self.item_option_commission_title = item_option_element.find('itemOptionCommissionTitle')
            self.item_option_commission_vals = [self.ItemOptionCommission(item_option_commission) for item_option_commission in item_option_element.findall('itemOptionCommissionVal')]
            self.item_option_commission_note = item_option_element.find('itemOptionCommissionNote')
            self.item_option_commission_seq = item_option_element.find('itemOptionCommissionSeq')

        class ItemOptionCommission:
            def __init__(self, item_option_cmmission_value_element):
                self.item_option_commission = item_option_cmmission_value_element.find('itemOptionCommission')
                self.item_option_commission_price = item_option_cmmission_value_element.find('itemOptionCommissionPrice') 
                self.item_option_commission_val_seq = item_option_cmmission_value_element.find('itemOptionCommissionValSeq')
    class RegisterStock:
        def __init__(self, register_stock_element):
            self.stock_segment = register_stock_element.find('stockSegment')
            self.stock_count = register_stock_element.find('stockCount')
            self.stock_shipping_day_id = register_stock_element.find('stockShippingDayId')
            self.stock_shipping_day_disp_txt = register_stock_element.find('stockShippingDayDispTxt')
            self.display_stock_segment = register_stock_element.find('displayStockSegment')
            self.display_stock_threshold = register_stock_element.find('displayStockThreshold')
            self.choices_stock_horizontal_item_name = register_stock_element.find('choicesStockHorizontalItemName')

            
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
            error_code = response_parsed.find('./result/error/code')
            error_message = response_parsed.find('./result/error/message')
            print(f'{error_code} {error_message}')
        else:
            items = response_parsed.findall('./searchResult/resultItems')
            for item in items:
                print(item)
            print(f'{len(items)} 件取得しました')
        
wowma_api = WowmaApi()

