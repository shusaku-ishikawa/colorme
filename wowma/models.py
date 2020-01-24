from django.db import models
import xml.etree.ElementTree as ET
from .enums import *

class AuthInfo(models.Model):
    def __str__(self):
        return self.application_key or ''
    application_key = models.CharField(
        max_length = 100,
        primary_key = True
    )
    store_id = models.CharField(
        max_length = 10,
    )


def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class XMLSerializable(object):
    def serialize(self):
        root = ET.Element(self.element_name)
        for k in vars(self):
            v = getattr(self, k)
            if not v:
                continue
            if type(v) == list:
                for child in v:
                    root.append(child.serialize())
            else:
                sub = ET.SubElement(root, to_camel_case(k))
                sub.text = v
        return root
# Create your models here.
class Item(XMLSerializable):
    element_name = 'registerItem'
    def __init__(self, item_element):
        if type(item_element) == str:
            self.lot_number = item_element
        else:
            print(type(item_element))
            self.lot_number = item_element.find('lotNumber').text
            self.item_name = item_element.find('itemName').text
            self.item_management_id = item_element.find('itemManagementId').text
            self.item_management_name = item_element.find('itemManagementName').text
            self.item_code = item_element.find('itemCode').text
            self.item_price = item_element.find('itemPrice').text
            self.sell_method_segment = item_element.find('sellMethodSegment').text
            self.release_date = item_element.find('releaseDate').text
            self.reserve_regst_date = item_element.find('reserveRegstDate').text
            self.tas_segment = item_element.find('taxSegment').text
            self.postage_segment = item_element.find('postageSegment').text
            self.postage = item_element.find('postage').text
            self.deliverys = [self.Delivery(delivery) for delivery in item_element.findall('deliverys') if delivery.getchildren()]
            self.delivery_method = [self.DeliveryMethod(delivery_method) for delivery_method in item_element.findall('deliveryMethod') if delivery_method.getchildren()]
            self.public_start_date = item_element.find('publicStartDate').text
            self.gift_packing_segment = item_element.find('giftPackingSegment').text
            self.noshi_segment = item_element.find('noshiSegment').text
            self.limited_order_segment = item_element.find('limitedOrderSegment').text
            self.limited_order_count = item_element.find('limitedOrderCount').text
            self.description = item_element.find('description').text
            self.description_forSP = item_element.find('descriptionForSP').text
            self.description_forPC = item_element.find('descriptionForPC').text
            self.detail_title = item_element.find('detailTitle').text
            self.detail_description = item_element.find('detailDescription').text
            self.specs = [self.Spec(spec) for spec in item_element.findall('specs') if spec.getchildren()]
            self.search_keywords = [self.SearchKeyword(search_keyword) for search_keyword in item_element.findall('searchKeywords') if search_keyword.getchildren()]
            self.images = [self.Image(image) for image in item_element.findall('images') if image.getchildren()]
            self.category_id = item_element.find('categoryId').text
            self.category_name = item_element.find('ctgryName').text
            self.tags = [self.Tag(tag) for tag in item_element.findall('tags') if tag.getchildren()]
            self.shop_categorys = [self.ShopCategory(shop_category) for shop_category in item_element.findall('shopCategory') if shop_category.getchildren()]
            self.jan = item_element.find('jan').text
            self.isbn = item_element.find('isbn').text
            self.item_model = item_element.find('itemModel').text
            self.limited_passwd = item_element.find('limitedPasswd').text
            self.limited_passwd_page_title = item_element.find('limitedPasswdPageTitle').text
            self.limited_passwd_page_messsage = item_element.find('limitedPasswdPageMessage').text
            self.sale_status = item_element.find('saleStatus').text
            self.item_options = [self.ItemOption(item_option) for item_option in item_element.findall('itemOptions') if item_option.getchildren()]
            self.item_option_commissions = [self.ItemOptionCommission(item_option_commission) for item_option_commission in item_element.findall('itemOptionCommissions') if item_option_commission.getchildren()]
            self.point_rate = item_element.find('pointRate').text
            self.favorite_count = item_element.find('favoriteCount').text
            self.receipt_request_count = item_element.find('receiptRequestCount').text
            self.stock_request_config = item_element.find('stockRequestConfig').text
            self.stock_request_count = item_element.find('stockRequestCount').text
            self.register_stocks = [self.RegisterStock(register_stock) for register_stock in item_element.findall('registerStock') if register_stock.getchildren()]
            print(len(self.register_stocks))
    class Delivery(XMLSerializable):
        element_name = 'deliverys'
        def __init__(self, delivery_element):
            self.delivery_id = delivery_element.find('deliveryId').text
            self.delivery_seq = delivery_element.find('deliverySeq').text
    class DeliveryMethod(XMLSerializable):
        element_name = 'deliveryMethod'
        def __init__(self, delivery_method_element):
            self.delivery_method_id = delivery_method_element.find('deliveryMethodId').text
            self.delivery_method_seq = delivery_method_element.find('deliveryMethodSeq').text
            self.delivery_method_name = delivery_method_element.find('deliveryMethodName').text
    class Spec(XMLSerializable):
        element_name = 'specs'
        def serialize(self):
            root = ET.Element(self.element_name)
            for k in vars(self):
                v = getattr(self, k)
                if type(v) == list:
                    for child in v:
                        root.append(child.serialize())
                else:
                    sub = ET.SubElement(root, to_camel_case(k))
                    sub.text = v
                subelem = ET.SubElement(root, to_camel_case(k))
                subelem.text = v
            return root
        def __init__(self, spec_element):
            self.spec_title = spec_element.find('specTitle').text
            self.detail_specs = [self.DetailSpec(detail_spec) for detail_spec in spec_element.findall('detailSpecs') if detail_spec.getchildren()]
        class DetailSpec:
            def serialize(self):
                root = ET.Element('detailSpecs')
                for k in vars(self):
                    v = getattr(self, k)
                    sub = ET.SubElement(root, to_camel_case(k))
                    sub.text = v
                return root
            def __init__(self, detail_spec):
                self.spec_name = detail_spec.find('specName').text
                self.spec = detail_spec.find('spec').text
                self.spec_seq = detail_spec.find('specSeq').text
    class SearchKeyword(XMLSerializable):
        element_name = 'searchKeywords'
        def __init__(self, search_keyword_element):
            self.search_keyword = search_keyword_element.find('searchKeyword').text
            self.search_keyword_seq = search_keyword_element.find('searchKeywordSeq').text
    class Image(XMLSerializable):
        element_name = 'images'
        def __init__(self, item_element):
            self.image_url = item_element.find('imageUrl').text
            self.image_name = item_element.find('imageName').text
            self.imange_seq = item_element.find('imageSeq').text
    class Tag(XMLSerializable):
        element_name = 'tags'
        def __init__(self, tag_element):
            self.tag_id = tag_element.find('tagId').text
    class ShopCategory(XMLSerializable):
        element_name = 'shopCategory'
        def __init__(self, shop_category_element):
            self.shop_category_name = shop_category_element.find('shopCategoryName').text if 'shopCategoryName' in shop_category_element else None
            self.shop_category_disp_seq = shop_category_element.find('shopCategoryDispSeq').text if 'shopCategoryDispSeq' in shop_category_element else None
    class ItemOption(XMLSerializable):
        element_name = 'itemOptions'
        def __init__(self, item_option_element):
            self.item_option_title = item_option_element.find('itemOptionTitle').text
            self.item_option = item_option_element.find('itemOption').text
            self.item_option_seq = item_option_element.find('itemOptionSeq').text
    class ItemOptionCommission(XMLSerializable):
        element_name = 'itemOptionCommissions'
        def __init__(self, item_option_element):
            self.item_option_commission_title = item_option_element.find('itemOptionCommissionTitle').text
            self.item_option_commission_vals = [self.ItemOptionCommission(item_option_commission) for item_option_commission in item_option_element.findall('itemOptionCommissionVal') if item_option_commission.getchildren()]
            self.item_option_commission_note = item_option_element.find('itemOptionCommissionNote').text
            self.item_option_commission_seq = item_option_element.find('itemOptionCommissionSeq').text

        class ItemOptionCommission(XMLSerializable):
            element_name = 'itemOptionCommissionVal'
            def __init__(self, item_option_cmmission_value_element):
                self.item_option_commission = item_option_cmmission_value_element.find('itemOptionCommission').text
                self.item_option_commission_price = item_option_cmmission_value_element.find('itemOptionCommissionPrice').text
                self.item_option_commission_val_seq = item_option_cmmission_value_element.find('itemOptionCommissionValSeq').text
    class RegisterStock(XMLSerializable):
        element_name = 'registerStock'
        def __init__(self, register_stock_element):
            self.stock_segment = register_stock_element.find('stockSegment').text
            self.stock_count = register_stock_element.find('stockCount').text if 'stockCount' in register_stock_element else None
            self.stock_shipping_day_id = register_stock_element.find('stockShippingDayId').text if 'stockShippingDayId' in register_stock_element else None
            self.stock_shipping_day_disp_txt = register_stock_element.find('stockShippingDayDispTxt').text if 'stockShippingDayDispTxt' in register_stock_element else None
            self.display_stock_segment = register_stock_element.find('displayStockSegment').text if 'displayStockSegment' in register_stock_element else None
            self.display_stock_threshold = register_stock_element.find('displayStockThreshold').text if 'displayStockThreshold' in register_stock_element else None
            self.choices_stock_horizontal_item_name = register_stock_element.find('choicesStockHorizontalItemName').text
            self.choices_stock_horizontals = [self.ChoicesStockHorizontal(choices_stock_horizontal) for choices_stock_horizontal in register_stock_element.findall('choicesStockHorizontals') if choices_stock_horizontal.getchildren()]
            self.choices_stock_vertical_item_name = register_stock_element.find('choicesStockVerticalItemName').text
            self.choices_stock_verticals = [self.ChoicesStockVertical(choices_stock_vertical) for choices_stock_vertical in register_stock_element.findall('choicesStockVerticals') if choices_stock_vertical.getchildren()]
            self.choices_stocks = [self.ChoicesStock(choices_stock) for choices_stock in register_stock_element.findall('choicesStocks') if choices_stock.getchildren()]
            self.choices_stock_upper_description = register_stock_element.find('choicesStockUpperDescription').text
            self.choices_stock_lower_description = register_stock_element.find('choicesStockLowerDescription').text
            self.display_choices_stock_segment = register_stock_element.find('displayChoicesStockSegment').text
            self.display_chioces_stock_threshold = register_stock_element.find('displayChoicesStockThreshold').text
            self.display_backorder_message = register_stock_element.find('displayBackorderMessage').text
            
        class ChoicesStockHorizontal(XMLSerializable):
            element_name = 'choicesStockHorizontals'
            def __init__(self, choices_stock_horiontal_element):
                self.choices_stock_horizontal_code = choices_stock_horiontal_element.find('choicesStockHorizontalCode').text
                self.choices_stock_horizontal_name = choices_stock_horiontal_element.find('choicesStockHorizontalName').text
                self.choices_stock_horizontal_seq = choices_stock_horiontal_element.find('choicesStockHorizontalSeq').text
        class ChoicesStockVertical(XMLSerializable):
            element_name = 'choicesStockVerticals' 
            def __init__(self, choices_stock_vertical_element):
                self.choices_stock_vertical_code = choices_stock_vertical_element.find('choicesStockVerticalCode').text
                self.choices_stock_vertical_name = choices_stock_vertical_element.find('choicesStockVerticalName').text
                self.choices_stock_vertical_seq = choices_stock_vertical_element.find('choicesStockVerticalSeq').text
        class ChoicesStock(XMLSerializable):
            element_name = 'choicesStocks'
            def __init__(self, choices_stock_element):
                self.choices_stock_horizontal_code = choices_stock_element.find('choicesStockHorizontalCode').text
                self.choices_stock_vertical_code = choices_stock_element.find('choicesStockVerticalCode').text
                self.choices_stock_count = choices_stock_element.find('choicesStockCount').text
                self.choices_stock_shipping_day_id = choices_stock_element.find('choicesStockShippingDayId').text
                self.chioces_stock_shipping_day_disp_txt = choices_stock_element.find('choicesStockShippingDayDispTxt').text
    
    def serialize_for_delete(self, shop_id):
        request = ET.Element('request')
        shop_id = ET.SubElement(request, 'shopId')
        shop_id.text = shop_id
        item_info = ET.SubElement(request, 'deleteItemInfo')
        lot_number = ET.SubElement(item_info, 'lotNumber')
        lot_number.text = self.lot_number
        return ET.dump(request)

    def serialize_for_add(self, shop_id):
        request = ET.Element('request')
        shop_id = ET.SubElement(request, 'shopId')
        shop_id.text = shop_id
        register_item = ET.SubElement(request, 'registerItem')
        for k in vars(self):
            v = getattr(self, k)
            print(f'{k} {v}')
    def delete(self, authinfo):
        print(self.serialize_for_add('hoge'))
        # url = f'{WOWMA_ENDPOINT}deleteItemInfos/'
        # response = requests.get(url, headers = self.get_headers(), proxies = __class__.proxies)

import math
class ItemSearchResult(object):
    def __init__(self, response_parsed, limit, page):
        self.status = response_parsed.find('./result/status').text
        if self.status != API_STATUS_SUCCESS:
            self.error = self.Error(response_parsed.find('./result/error')) 
            self.pagination = self.Pagination(5, page, 110)
            print('error')          
        else:
            result_count = response_parsed.find('./searchResult/resultCount').text
            max_count = response_parsed.find('./searchResult/maxCount').text
            self.pagination = self.Pagination(limit, page, int(max_count))            
            self.items = [Item(item) for item in response_parsed.findall('./searchResult/resultItems')]
            self.max_count = max_count
    class Error(object):
        def __init__(self, error_element):
            self.code = error_element.find('code').text
            self.message = error_element.find('message').text

    class Pagination(object):
        max_display_pages = 10
        def __init__(self, items_per_page, current_page, max_count):
            self.item_per_page = items_per_page
            self.current_page = current_page
            self.max_count = max_count
            self.total_pages = math.ceil(max_count / items_per_page)
            self.init_display_list()
        @property
        def has_next(self):
            return self.total_pages > self.current_page
        @property
        def has_previous(self):
            return self.current_page > 1
        @property
        def first_index_hidden(self):
            return (self.display_list[0] != 1) if len(self.display_list) > 0 else False
        @property
        def last_index_hidden(self):
            return (self.display_list[len(self.display_list) - 1] != self.total_pages) if len(self.display_list) > 0 else False
        
        def init_display_list(self):
            display_count = self.total_pages if self.total_pages < __class__.max_display_pages else __class__.max_display_pages
            
            if (display_count - 3) % 2 == 0:
                left_offset = int((display_count - 3) / 2)
                right_offset = int((display_count - 3) / 2)
            else:
                left_offset = int((display_count - 4) / 2)
                right_offset = int((display_count - 2) / 2)
                
            if (self.current_page - left_offset) < 1:
                print('margin')
                margin = left_offset - (self.current_page - 1)
                print(margin)
                left_offset -= margin
                right_offset += margin
           
            self.display_list = [index for index in range(self.current_page - left_offset, self.current_page + right_offset + 1)]

class UploadFileColumns(object):
    ctrl_col = 0
    lot_number = 1
    item_name = 2
    item_management_id = 3
    item_management_name = 4
    item_code = 5
    item_price = 6
    sell_method_segment = 7
    release_date = 8
    maker_retail_price = 9
    maker_retail_price_url = 10
    tax_segment = 11
    reduced_tax = 12
    postage_segment = 13
    postage = 14
    delivery_id = 15
    delivery_method_id_start = 16
    delivery_method_name_start = 21
    sell_start_date = 26
    sell_end_date = 27
    countdown_timer_config = 28
    sell_number_disp_config = 29
    buy_num_limit_config = 30
    buy_num_max = 31
    public_start_date = 32
    gift_packing_segment = 33
    noshi_segment = 34
    limited_order_segment = 35
    limited_order_count = 36
    description = 37
    description_for_sp = 38
    description_for_pc = 39
    detail_title = 40
    detail_description = 41
    spec_title = 42
    spec_start = 43
    search_keyword_start = 48
    search_target = 51
    image_name_start = 52
    image_url_start = 72




