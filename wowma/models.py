from django.db import models
import xml.etree.ElementTree as ET
from .enums import *
import csv

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

class SerializableModel(models.Model):
    columns = []
    node_name = ''
    def set_attributes(self, element):
        for column_name, column_type in self.columns:
            elem = element.find(column_name)
            if elem != None and elem.text != None:
                setattr(self, column_name, column_type(elem.text))
        self.save()
    
    def serialize(self, mode = API_MODE_REGISTER):
        root = ET.Element(self.node_name)
        for column_name, _ in self.columns:
            elem = ET.SubElement(root, column_name)
            elem.text = getattr(self, column_name)
        return root

class Category(SerializableModel):
    columns = [
        ('ctgryId', int),
        ('ctgryNameFullpath', str)
    ]
    ctgryId = models.IntegerField()
    ctgryNameFullpath = models.CharField(max_length = 255)
    
class ShopCategory(SerializableModel):
    columns = [
        ('shopCategoryId', int),
        ('shopCategoryLevel', str),
        ('shopCategoryName', str)        
    ]
    user = models.ForeignKey(to = 'core.User', on_delete = models.CASCADE, related_name = 'wowma_categories')
    shopCategoryId = models.IntegerField(unique = True)
    shopCategoryLevel = models.CharField(max_length = 1)
    shopCategoryName = models.CharField(max_length = 255)
    
    @property
    def category_list(self):
        return self.shopCategoryName.split(':')
class Item(SerializableModel):
    columns = [
        ('lotNumber', int),
        ('itemName', str),
        ('itemManagementId', str),
        ('itemManagementName', str),
        ('itemCode', str),
        ('itemPrice', int),
        ('sellMethodSegment', str),
        ('taxSegment', str),
        ('postageSegment', str),
        ('description', str),
        ('descriptionForSP', str),
        ('descriptionForPC', str),
        ('categoryId', str),
        ('saleStatus', str)
    ]
    user = models.ForeignKey(to = 'core.User', on_delete = models.CASCADE, related_name = 'wowma_items')
    lotNumber = models.IntegerField(unique = True, null = True)
    itemName = models.CharField(max_length = 128)
    itemManagementId = models.CharField(max_length = 128, null = True, blank = True)
    itemManagementName = models.CharField(max_length = 128, null = True, blank = True)
    itemCode = models.CharField(max_length = 128, null = True, blank = True)
    itemPrice = models.IntegerField()
    sellMethodSegment = models.CharField(max_length = 1, default = '1')
    taxSegment = models.CharField(max_length = 1, default = '1')
    postageSegment = models.CharField(max_length = 1, default = '2')
    description = models.TextField()
    descriptionForSP = models.TextField()
    descriptionForPC = models.TextField()
    categoryId = models.CharField(max_length = 20, null = True, blank = True)
    saleStatus = models.CharField(max_length = 1, default = '1')
    
    def set_attributes(self, item_element):
        super().set_attributes(item_element)

        for image_element in item_element.findall('images'):
            image = Image(parent_item = self)
            image.set_attributes(image_element)
         
        register_stock = RegisterStock(parent_item = self)
        if item_element.find('registerStock'):
            register_stock.set_attributes(item_element.find('registerStock'))

        self.save()
        return True

    def serialize(self, mode = API_MODE_REGISTER):
        root = ET.Element(f'{mode}Item')
        for column_name, _ in self.columns:
            elem = ET.SubElement(root, column_name)
            elem.text = getattr(slef, column_name)
        
        for image in self.images:
            root.append(image.serialize())
        return root
    
    def delete_request_param(self, shop_id):
        root = ET.Element('request')
        shop_id = ET.SubElement(root, 'shopId')
        shop_id.text = shop_id
        delete_item_info = ET.SubElement(root, 'deleteItemInfo')
        lotnumber = ET.SubElement(delete_item_info, 'lotNumber')
        lotnumber.text = self.lotNumber
        return ET.tostring(root, encoding='utf-8')

    @property
    def category_name(self):
        if self.categoryId:
            category = Category.objects.get(ctgryId = self.categoryId)
            return category.ctgryNameFullpath

class ItemShopCategory(SerializableModel):
    columns = [
        ('shopCategoryName', str),
        ('shopCategoryDispSeq', str)
    ]
    parent_item = models.ForeignKey(to = Item, on_delete = models.CASCADE, related_name = 'shopCategories')
    shopCategory = models.ForeignKey(to = ShopCategory, on_delete = models.CASCADE, related_name = 'items')

class Image(SerializableModel):
    columns = [
        ('imageUrl', str),
        ('imageName', str),
        ('imageSeq', str)
    ]
    node_name = 'images'

    parent_item = models.ForeignKey(to = Item, on_delete = models.CASCADE, related_name = 'images')
    imageUrl = models.URLField(max_length = 255)
    imageName = models.CharField(max_length = 16)
    imageSeq = models.CharField(max_length = 2)

class RegisterStock(SerializableModel):
    columns = [
        ('stockSegment', str),
        ('stockCount', str),
        ('choicesStockHorizontalItemName', str),
        ('choicesStockVerticalItemName', str)
    ]
    
    parent_item = models.OneToOneField(to = Item, on_delete = models.CASCADE)
    stockSegment = models.CharField(max_length = 1)
    stockCount = models.CharField(max_length = 5, null = True, blank = True)
    choicesStockHorizontalItemName = models.CharField(max_length = 50)
    choicesStockVerticalItemName = models.CharField(max_length = 50)
    
    def set_attributes(self, register_stock_element):
        super().set_attributes(register_stock_element)

        for horizontal_element in register_stock_element.findall('choicesStockHorizontals'):
            horizontal = ChoicesStockHorizontal(registerStock = self)
            horizontal.set_attributes(horizontal_element)
        
        for vertical_element in register_stock_element.findall('choicesStockVerticals'):
            vertical = ChoicesStockVertical(registerStock = self)
            vertical.set_attributes(vertical_element)
        
        for choices_stock_element in register_stock_element.findall('choicesStocks'):
            choices_stock = ChoicesStock(registerStock = self)
            choices_stock.set_attributes(choices_stock_element)

        return True
        
    def serialize(self, mode = API_MODE_REGISTER):
        root = ET.Element(f'{mode}Stock')
        
        for column_name, _ in self.columns:
            elem = ET.SubElement(root, column_name)
            elem.text = getattr(self, column_name)
        
        for hor in self.horizontals.all():
            root.append(hor.serialize())

        for ver in self.verticals.all():
            root.append(ver.serialize())

        for choicesStock in self.chiocesStocks.all():
            root.append(chiocesStocks.serialize())

        return root

class ChoicesStockHorizontal(SerializableModel):
    columns = [
        ('choicesStockHorizontalCode', str),
        ('choicesStockHorizontalName', str),
        ('choicesStockHorizontalSeq', str),
    ]
    node_name = 'chiocesStockHorizontals'

    registerStock = models.ForeignKey(to = RegisterStock, on_delete = models.CASCADE, related_name = 'horizontals')
    choicesStockHorizontalCode = models.CharField(max_length = 255)
    choicesStockHorizontalName = models.CharField(max_length = 100)
    choicesStockHorizontalSeq = models.CharField(max_length = 2)
    
class ChoicesStockVertical(SerializableModel):
    columns = [
        ('choicesStockVerticalCode', str),
        ('choicesStockVerticalName', str),
        ('choicesStockVerticalSeq', str),
    ]
    node_name = 'choicesStockVerticals'


    registerStock = models.ForeignKey(to = RegisterStock, on_delete = models.CASCADE, related_name = 'verticals')
    choicesStockVerticalCode = models.CharField(max_length = 255)
    choicesStockVerticalName = models.CharField(max_length = 100)
    choicesStockVerticalSeq = models.CharField(max_length = 2)

        
class ChoicesStock(SerializableModel):
    columns = [
        ('choicesStockVerticalCode', str),
        ('choicesStockHorizontalCode', str),
        ('choicesStockCount', str)
    ]
    node_name = 'choicesStocks'

    registerStock = models.ForeignKey(to = RegisterStock, on_delete = models.CASCADE, related_name = 'choicesStocks')
    choicesStockVerticalCode = models.CharField(max_length = 255)
    choicesStockHorizontalCode = models.CharField(max_length = 255)
    choicesStockCount = models.CharField(max_length = 5)
    
import cgi
def xml_escape(s):
    return cgi.escape(s)

# class XMLSerializable(object):
#     excludes_to_serialize = [
#         'error',
#         'valid',
#         'line_number',
#         'required_for_add'
#     ]

#     def validate_for_add(self, index):
#         self.valid = True
#         print(f'validating {self.__class__}')
#         if 'required_for_add' not in list(vars(self)):
#             self.required_for_add = list(vars(self))
#         self.line_number = index
#         for f in self.required_for_add:
#             if not f in vars(self):
#                 self.valid = False
#                 self.error = f'[{self.__class__}]{f}は必須です'
#                 return self.valid
#             val = getattr(self, f)
#             if val == None:
#                 self.valid = False
#                 self.error = f'[{self.__class__}]{f}は必須です'
#                 return self.valid
#             elif type(val) == list:
#                 for obj in val:
#                     if obj.validate_for_add(index) == False:
#                         self.valid = False
#                         self.error = obj.error
#                         return self.valid   
#         return self.valid
#     def serialize(self, mode = API_MODE_REGISTER):
#         if self.__class__ in [Item, Item.RegisterStock]:
#             if mode == API_MODE_REGISTER:
#                 element_name = f'{mode}Item' if self.__class__ == Item else f'{mode}Stock'
#             elif mode == API_MODE_UPDATE:
#                 element_name = f'{mode}Item' if self.__class__ == Item else f'{mode}Stock'
#             elif mode == API_MDOE_DELETE:
#                 element_name = f'{mode}ItemInfo' if self.__class__ == Item else f'{mode}Stock'
#             else:
#                 raise Exception('invalid serialize mode')
#         else:
#             element_name = self.element_name
#         root = ET.Element(element_name)
#         for k in vars(self):
#             if k in self.excludes_to_serialize:
#                 continue
#             v = getattr(self, k)
#             if not v:
#                 continue
#             if type(v) == list:
#                 for child in v:
#                     root.append(child.serialize())
#             else:
#                 if k == 'description_forSP':
#                     field_name = 'descriptionForSP'
#                 elif k == 'description_forPC':
#                     field_name = 'descriptionForPC'
#                 else:
#                     field_name = to_camel_case(k)

#                 sub = ET.SubElement(root, field_name)
#                 sub.text = v
        
#         return root
# # Create your models here.
# class Itemobj(XMLSerializable):
#     element_name = 'registerItem'
#     required_for_add = [
#         'item_name',
#         'item_code',
#         'item_price',
#         'tax_segment',
#         'postage_segment',
#         'description',
#         'category_id',
#         'sale_status',
#         'register_stocks'
#     ]
#     def __str__(self):
#         root = self.serialize()
#         return ET.tostring(self.serialize(), encoding='utf-8').decode('utf-8')

#     def __init__(self):
#         pass
#     def __init__(self, item_element):
#         if type(item_element) == str:
#             self.lot_number = item_element
#         elif isinstance(item_element, list):
#             self.item_name = item_element[ItemCols.ITEM_NAME]
#             self.item_management_id = item_element[ItemCols.ITEM_MANAGEMENT_ID]
#             self.item_management_name = item_element[ItemCols.ITEM_MANAGEMENT_NAME]
#             self.item_code = item_element[ItemCols.ITEM_CODE]
#             self.item_price = item_element[ItemCols.ITEM_PRICE]
#             self.sell_method_segment = item_element[ItemCols.SELL_METHOD_SEGMENT]
#             self.release_date = item_element[ItemCols.RELEASE_DATE]
#             self.tax_segment = item_element[ItemCols.TAX_SEGMENT]
#             self.postage_segment = item_element[ItemCols.POSTAGE_SEGMENT]
#             self.postage = item_element[ItemCols.POSTAGE]
#             self.delivery_method = [self.DeliveryMethod({'delivery_method_id': item_element[ItemCols.DELIVERY_METHOD_ID_START + i], 'delivery_method_name': item_element[ItemCols.DELIVERY_METHOD_NAME_START + i], 'delivery_method_seq': str(i + 1)}) for i in range(5) if item_element[ItemCols.DELIVERY_METHOD_ID_START + i]]
#             self.public_start_date = item_element[ItemCols.PUBLIC_START_DATE]
#             self.gift_packing_segment = item_element[ItemCols.GIFT_PACKING_SEGMENT]
#             self.noshi_segment = item_element[ItemCols.NOSHI_SEGMENT]
#             self.limited_order_segment = item_element[ItemCols.LIMITED_ORDER_SEGMENT]
#             self.limited_order_count = item_element[ItemCols.LIMITED_ORDER_COUNT]
#             self.description = item_element[ItemCols.DESCRIPTION]
#             self.description_forSP = item_element[ItemCols.DESCRIPTION_FORSP]
#             self.description_forPC = item_element[ItemCols.DESCRIPTION_FORPC]
#             self.detail_title = item_element[ItemCols.DETAIL_TITLE]
#             self.detail_description = item_element[ItemCols.DETAIL_DESCRIPTION]
#             self.specs = [self.Spec({'spec_title': item_element[ItemCols.SPEC_TITLE], 'detail_spec': [item_element[ItemCols.SPEC_START + i]]}) for i in range(5) if item_element[ItemCols.SPEC_START + i]]
#             self.search_keyword = [self.SearchKeyword({'search_keyword': item_element[ItemCols.SEARCH_KEYWORD_START + i], 'search_keyword_seq': str(i + 1)}) for i in range(3) if item_element[ItemCols.SEARCH_KEYWORD_START + i]]
#             self.images = [self.Image({'image_name': item_element[ItemCols.IMAGE_NAME_START + i], 'image_url': item_element[ItemCols.IMAGE_URL_START + i], 'image_seq': str(i+1) }) for i in range(20) if item_element[ItemCols.IMAGE_URL_START + i]]
#             self.category_id = item_element[ItemCols.CATEGORY_ID]
#             self.tags = [self.Tag({'tag_id': tag_id}) for tag_id in item_element[ItemCols.TAG_ID].split('/') if item_element[ItemCols.TAG_ID]]
#             self.shop_categorys = [self.ShopCategory({'shop_category_name': item_element[ItemCols.SHOP_CATEGORY_ID_START + i], 'shop_category_disp_seq': str(i+i)}) for i in range(10) if item_element[ItemCols.SHOP_CATEGORY_ID_START + i]]
#             self.shop_category_disp_seq = item_element[ItemCols.SHOP_CATEGORY_DISP_SEQ]
#             self.jan = item_element[ItemCols.JAN]
#             self.isbn = item_element[ItemCols.ISBN]
#             self.item_model = item_element[ItemCols.ITEM_MODEL]
#             self.limited_passwd = item_element[ItemCols.LIMITED_PASSWD]
#             self.limited_passwd_page_title = item_element[ItemCols.LIMITED_PASSWD_PAGE_TITLE]
#             self.limited_passwd_page_message = item_element[ItemCols.LIMITED_PASSWD_PAGE_MESSAGE]
#             self.sale_status = item_element[ItemCols.SALE_STATUS]
#             self.cross_border_ec_lnk_config = item_element[ItemCols.CROSS_BORDER_EC_LNK_CONFIG]
#             self.item_options = [self.ItemOption({'item_option': f'{i + 1}:{item_element[ItemCols.ITEM_OPTION_START + i]}'}) for i in range(20) if item_element[ItemCols.ITEM_OPTION_START + i]]           
#             self.item_option_commissions = [self.ItemOptionCommission({'item_option_commission_title': item_element[ItemCols.ITEM_OPTION_COMMISSION_START + 3*i], 'item_option_commission_val': item_element[ItemCols.ITEM_OPTION_COMMISSION_START + 3*i + 1], 'item_option_commitssion_note': item_element[ItemCols.ITEM_OPTION_COMMISSION_START + 3*i + 2], 'item_option_commission_seq': i+i}) for i in range(20) if item_element[ItemCols.ITEM_OPTION_COMMISSION_START + 3*i]]
#             self.point_rate = item_element[ItemCols.POINT_RATE]
#             self.stock_request_config = item_element[ItemCols.STOCK_REQUEST_CONFIG]
#             register_stock_dict = {
#                 'stock_segment': item_element[ItemCols.STOCK_SEGMENT],
#                 'display_backorder_message': item_element[ItemCols.DISPLAY_BACKORDER_MESSAGE],
#                 'stock_count': item_element[ItemCols.STOCK_COUNT],
#                 'stock_shipping_day_id': item_element[ItemCols.STOCK_SHIPPING_DAY_ID],
#                 'display_stock_segment': item_element[ItemCols.DISPLAY_STOCK_SEGMENT],
#                 'display_stock_threshold': item_element[ItemCols.DISPLAY_STOCK_THRESHOLD],
#                 'choices_stock_horizontal_item_name': item_element[ItemCols.CHOICES_STOCK_HORIZONTAL_ITEM_NAME],
#                 'choices_stock_vertical_item_name': item_element[ItemCols.CHOICES_STOCK_VERTICAL_ITEM_NAME],
#                 'choices_stock_upper_description': item_element[ItemCols.CHOICES_STOCK_UPPER_DESCRIPTION],
#                 'choices_stock_lower_description': item_element[ItemCols.CHOICES_STOCK_LOWER_DESCRIPTION],
#                 'display_choices_stock_segment': item_element[ItemCols.DISPLAY_CHOICES_STOCK_SEGMENT],
#                 'display_choices_stock_threshold': item_element[ItemCols.DISPLAY_CHOICES_STOCK_THRESHOLD]
#             }
#             self.register_stocks = [self.RegisterStock(register_stock_dict)]

#         elif isinstance(item_element, ET.Element):
            
#             self.lot_number = item_element.find('lotNumber').text
#             self.item_name = item_element.find('itemName').text
#             self.item_management_id = item_element.find('itemManagementId').text
#             self.item_management_name = item_element.find('itemManagementName').text
#             self.item_code = item_element.find('itemCode').text
#             self.item_price = item_element.find('itemPrice').text
#             self.sell_method_segment = item_element.find('sellMethodSegment').text
#             self.release_date = item_element.find('releaseDate').text
#             self.reserve_regst_date = item_element.find('reserveRegstDate').text
#             self.tas_segment = item_element.find('taxSegment').text
#             self.postage_segment = item_element.find('postageSegment').text
#             self.postage = item_element.find('postage').text
#             self.deliverys = [self.Delivery(delivery) for delivery in item_element.findall('deliverys') if delivery.getchildren()]
#             self.delivery_method = [self.DeliveryMethod(delivery_method) for delivery_method in item_element.findall('deliveryMethod') if delivery_method.getchildren()]
#             self.public_start_date = item_element.find('publicStartDate').text
#             self.gift_packing_segment = item_element.find('giftPackingSegment').text
#             self.noshi_segment = item_element.find('noshiSegment').text
#             self.limited_order_segment = item_element.find('limitedOrderSegment').text
#             self.limited_order_count = item_element.find('limitedOrderCount').text
#             self.description = item_element.find('description').text
#             self.description_forSP = item_element.find('descriptionForSP').text
#             self.description_forPC = item_element.find('descriptionForPC').text
#             self.detail_title = item_element.find('detailTitle').text
#             self.detail_description = item_element.find('detailDescription').text
#             self.specs = [self.Spec(spec) for spec in item_element.findall('specs') if spec.getchildren()]
#             self.search_keywords = [self.SearchKeyword(search_keyword) for search_keyword in item_element.findall('searchKeywords') if search_keyword.getchildren()]
#             self.images = [self.Image(image) for image in item_element.findall('images') if image.getchildren()]
#             self.category_id = item_element.find('categoryId').text
#             self.category_name = item_element.find('ctgryName').text
#             self.tags = [self.Tag(tag) for tag in item_element.findall('tags') if tag.getchildren()]
#             self.shop_categorys = [self.ShopCategory(shop_category) for shop_category in item_element.findall('shopCategory') if shop_category.getchildren()]
#             self.jan = item_element.find('jan').text
#             self.isbn = item_element.find('isbn').text
#             self.item_model = item_element.find('itemModel').text
#             self.limited_passwd = item_element.find('limitedPasswd').text
#             self.limited_passwd_page_title = item_element.find('limitedPasswdPageTitle').text
#             self.limited_passwd_page_messsage = item_element.find('limitedPasswdPageMessage').text
#             self.sale_status = item_element.find('saleStatus').text
#             self.item_options = [self.ItemOption(item_option) for item_option in item_element.findall('itemOptions') if item_option.getchildren()]
#             self.item_option_commissions = [self.ItemOptionCommission(item_option_commission) for item_option_commission in item_element.findall('itemOptionCommissions') if item_option_commission.getchildren()]
#             self.point_rate = item_element.find('pointRate').text
#             self.favorite_count = item_element.find('favoriteCount').text
#             self.receipt_request_count = item_element.find('receiptRequestCount').text
#             self.stock_request_config = item_element.find('stockRequestConfig').text
#             self.stock_request_count = item_element.find('stockRequestCount').text
#             self.register_stocks = [self.RegisterStock(register_stock) for register_stock in item_element.findall('registerStock') if register_stock.getchildren()]
#     class Delivery(XMLSerializable):
#         element_name = 'deliverys'
#         def __init__(self, delivery_element):
#             self.delivery_id = delivery_element.find('deliveryId').text
#             self.delivery_seq = delivery_element.find('deliverySeq').text
#     class DeliveryMethod(XMLSerializable):
#         element_name = 'deliveryMethod'
#         def __init__(self, delivery_method_element):
#             if isinstance(delivery_method_element, dict):
#                 self.delivery_method_id = delivery_method_element['delivery_method_id']
#                 self.delivery_method_name = delivery_method_element['delivery_method_name']
#                 self.delivery_method_seq = delivery_method_element['delivery_method_seq']

#             elif isinstance(delivery_method_element, ET.Element):
#                 self.delivery_method_id = delivery_method_element.find('deliveryMethodId').text
#                 self.delivery_method_seq = delivery_method_element.find('deliveryMethodSeq').text
#                 self.delivery_method_name = delivery_method_element.find('deliveryMethodName').text
#     class Spec(XMLSerializable):
#         element_name = 'specs'
#         def __init__(self, spec_element):
#             if isinstance(spec_element, dict):
#                 self.spec_title = spec_element['spec_title']
#                 self.detail_specs = [self.DetailSpec(f'{i + 1}:{v}') for i, v in enumerate(spec_element['detail_spec'])]
#             elif isinstance(spec_element, ET.Element):
#                 self.spec_title = spec_element.find('specTitle').text
#                 self.detail_specs = [self.DetailSpec(detail_spec) for detail_spec in spec_element.findall('detailSpecs') if detail_spec.getchildren()]
#         class DetailSpec(XMLSerializable):
#             element_name = 'detailSpecs'
#             def __init__(self, detail_spec):
#                 if isinstance(detail_spec, str):
#                     values = detail_spec.split(':')
#                     if len(values) == 3:
#                         self.spec_name = values[1]
#                         self.spec = values[3]
#                         self.spec_seq = values[0]
#                     elif len(values) == 2:
#                         self.spec_seq = values[0]
#                         ## to be deleted
#                 elif isinstance(detail_spec, ET.Element):
#                     self.spec_name = detail_spec.find('specName').text
#                     self.spec = detail_spec.find('spec').text
#                     self.spec_seq = detail_spec.find('specSeq').text
#     class SearchKeyword(XMLSerializable):
#         element_name = 'searchKeywords'
#         def __init__(self, search_keyword_element):
#             if isinstance(search_keyword_element, dict):
#                 self.search_keyword = search_keyword_element['search_keyword']
#                 self.search_keyword_seq = search_keyword_element['search_keyword_seq']
#             elif isinstance(search_keyword_element, ET.Element):
#                 self.search_keyword = search_keyword_element.find('searchKeyword').text
#                 self.search_keyword_seq = search_keyword_element.find('searchKeywordSeq').text
#     class Image(XMLSerializable):
#         element_name = 'images'
#         def __init__(self, image_element):
#             if isinstance(image_element, dict):
#                 self.image_url = image_element['image_url']
#                 self.image_name = image_element['image_name']
#                 self.image_seq = image_element['image_seq']
#             elif isinstance(image_element, ET.Element):
#                 self.image_url = image_element.find('imageUrl').text
#                 self.image_name = image_element.find('imageName').text
#                 self.imange_seq = image_element.find('imageSeq').text
#     class Tag(XMLSerializable):
#         element_name = 'tags'
#         def __init__(self, tag_element):
#             if isinstance(tag_element, dict):
#                 self.tag_id = tag_element['tag_id']
#             elif isinstance(tag_element, ET.Element):
#                 self.tag_id = tag_element.find('tagId').text
#     class ShopCategory(XMLSerializable):
#         element_name = 'shopCategory'
#         def __init__(self, shop_category_element):
#             if isinstance(shop_category_element, dict):
#                 self.shop_category_name = shop_category_element['shop_category_name']
#                 self.shop_category_disp_seq = shop_category_element['shop_category_disp_seq']
#             elif isinstance(shop_category_element, ET.Element):
#                 self.shop_category_name = shop_category_element.find('shopCategoryName').text if 'shopCategoryName' in shop_category_element else None
#                 self.shop_category_disp_seq = shop_category_element.find('shopCategoryDispSeq').text if 'shopCategoryDispSeq' in shop_category_element else None
#     class ItemOption(XMLSerializable):
#         element_name = 'itemOptions'
#         def __init__(self, item_option_element):
#             if isinstance(item_option_element, dict):
#                 values = item_option_element['item_option'].split(':')
#                 if len(values) == 3:
#                     self.item_option_title = values[1]
#                     self.item_option = values[2]
#                     self.item_option_seq = values[0]
#                 else:
#                     raise Exception(f'invalid item option {values}' )
#             elif isinstance(item_option_element, ET.Element):
#                 self.item_option_title = item_option_element.find('itemOptionTitle').text
#                 self.item_option = item_option_element.find('itemOption').text
#                 self.item_option_seq = item_option_element.find('itemOptionSeq').text
#     class ItemOptionCommission(XMLSerializable):
#         element_name = 'itemOptionCommissions'
#         def __init__(self, item_option_element):
#             if isinstance(item_option_element, dict):
#                 self.item_option_commission_title = item_option_element['item_option_commission_title']
#                 item_option_commission_values = item_option_element['item_option_commission_val'].split(':')
#                 if len(item_option_commission_values)%2 != 0:
#                     raise Exception('item option length invalid')
#                 self.item_option_commission_vals = [self.ItemOptionCommissionVal({'item_option_commission': item_option_commission_values[2*i], 'item_option_commission_price': item_option_commission_values[2*i + 1], 'item_option_commission_val_seq': i+1 }) for i in range(len(item_option_commission_values)/2)]
#                 self.item_option_commission_note = item_option_element['item_option_commission_note']
#                 self.item_option_commissoin_seq = item_option_element['item_option_commission_seq']
#             elif isinstance(item_option_element, ET.Element):
#                 self.item_option_commission_title = item_option_element.find('itemOptionCommissionTitle').text
#                 self.item_option_commission_vals = [self.ItemOptionCommissionVal(item_option_commission) for item_option_commission in item_option_element.findall('itemOptionCommissionVal') if item_option_commission.getchildren()]
#                 self.item_option_commission_note = item_option_element.find('itemOptionCommissionNote').text
#                 self.item_option_commission_seq = item_option_element.find('itemOptionCommissionSeq').text

#         class ItemOptionCommissionVal(XMLSerializable):
#             element_name = 'itemOptionCommissionVal'
#             def __init__(self, item_option_commission_value_element):
#                 if isinstance(item_option_commission_value_element, dict):
#                     self.item_option_commission = item_option_commission_value_element['item_option_commission']
#                     self.item_option_commission_price = item_option_commission_value_element['item_option_commission_price']
#                     self.item_option_commission_val_seq = item_option_commission_value_element['item_option_commission_val_seq']
#                 elif isinstance(item_option_commission_value_element, ET.Element):
#                     self.item_option_commission = item_option_commission_value_element.find('itemOptionCommission').text
#                     self.item_option_commission_price = item_option_commission_value_element.find('itemOptionCommissionPrice').text
#                     self.item_option_commission_val_seq = item_option_commission_value_element.find('itemOptionCommissionValSeq').text
#     class RegisterStock(XMLSerializable):
#         element_name = 'registerStock'

#         def __init__(self, register_stock_element):
#             # override
              
#             if isinstance(register_stock_element, dict):
#                 self.stock_segment = register_stock_element['stock_segment']
#                 self.stock_count = register_stock_element['stock_count']
#                 self.stock_shipping_day_id = register_stock_element['stock_shipping_day_id']
#                 self.display_stock_segment = register_stock_element['display_stock_segment']
#                 self.display_stock_threshold = register_stock_element['display_stock_threshold']
#                 self.choices_stock_horizontal_item_name = register_stock_element['choices_stock_horizontal_item_name']
#                 self.choices_stock_vertical_item_name = register_stock_element['choices_stock_vertical_item_name']
#                 self.choices_stock_upper_description = register_stock_element['choices_stock_upper_description']
#                 self.choices_stock_lower_description = register_stock_element['choices_stock_lower_description']
#                 self.display_choices_stock_segment = register_stock_element['display_choices_stock_segment']
#                 self.display_choices_stock_threshold = register_stock_element['display_choices_stock_threshold']

#             elif isinstance(register_stock_element, ET.Element):
#                 self.stock_segment = register_stock_element.find('stockSegment').text
#                 self.stock_count = register_stock_element.find('stockCount').text if 'stockCount' in register_stock_element else None
#                 self.stock_shipping_day_id = register_stock_element.find('stockShippingDayId').text if 'stockShippingDayId' in register_stock_element else None
#                 self.stock_shipping_day_disp_txt = register_stock_element.find('stockShippingDayDispTxt').text if 'stockShippingDayDispTxt' in register_stock_element else None
#                 self.display_stock_segment = register_stock_element.find('displayStockSegment').text if 'displayStockSegment' in register_stock_element else None
#                 self.display_stock_threshold = register_stock_element.find('displayStockThreshold').text if 'displayStockThreshold' in register_stock_element else None
#                 self.choices_stock_horizontal_item_name = register_stock_element.find('choicesStockHorizontalItemName').text
#                 self.choices_stock_horizontals = [self.ChoicesStockHorizontal(choices_stock_horizontal) for choices_stock_horizontal in register_stock_element.findall('choicesStockHorizontals') if choices_stock_horizontal.getchildren()]
#                 self.choices_stock_vertical_item_name = register_stock_element.find('choicesStockVerticalItemName').text
#                 self.choices_stock_verticals = [self.ChoicesStockVertical(choices_stock_vertical) for choices_stock_vertical in register_stock_element.findall('choicesStockVerticals') if choices_stock_vertical.getchildren()]
#                 self.choices_stocks = [self.ChoicesStock(choices_stock) for choices_stock in register_stock_element.findall('choicesStocks') if choices_stock.getchildren()]
#                 self.choices_stock_upper_description = register_stock_element.find('choicesStockUpperDescription').text
#                 self.choices_stock_lower_description = register_stock_element.find('choicesStockLowerDescription').text
#                 self.display_choices_stock_segment = register_stock_element.find('displayChoicesStockSegment').text
#                 self.display_chioces_stock_threshold = register_stock_element.find('displayChoicesStockThreshold').text
#                 self.display_backorder_message = register_stock_element.find('displayBackorderMessage').text
#         class ChoicesStockHorizontal(XMLSerializable):
#             element_name = 'choicesStockHorizontals'

#             def __init__(self, choices_stock_horizontal_element):
#                 if isinstance(choices_stock_horizontal_element, dict):
#                     self.choices_stock_horizontal_code = choices_stock_horizontal_element['choices_stock_horizontal_code']
#                     self.choices_stock_horizontal_name = choices_stock_horizontal_element['choices_stock_horizontal_name']
#                     self.choices_stock_horizontal_seq = choices_stock_horizontal_element['choices_stock_horizontal_seq']
                    
#                 elif isinstance(choices_stock_horizontal_element, ET.Element):
#                     self.choices_stock_horizontal_code = choices_stock_horizontal_element.find('choicesStockHorizontalCode').text
#                     self.choices_stock_horizontal_name = choices_stock_horizontal_element.find('choicesStockHorizontalName').text
#                     self.choices_stock_horizontal_seq = choices_stock_horizontal_element.find('choicesStockHorizontalSeq').text
            
#         class ChoicesStockVertical(XMLSerializable):
#             element_name = 'choicesStockVerticals' 
#             def __init__(self, choices_stock_vertical_element):
#                 if isinstance(choices_stock_vertical_element, dict):
#                     self.choices_stock_vertical_code = choices_stock_vertical_element['choices_stock_vertical_code']
#                     self.choices_stock_vertical_name = choices_stock_vertical_element['choices_stock_vertical_name']
#                     self.choices_stock_vertical_seq = choices_stock_vertical_element['choices_stock_vertical_seq']
#                 elif isinstance(choices_stock_vertical_element, ET.Element):        
#                     self.choices_stock_vertical_code = choices_stock_vertical_element.find('choicesStockVerticalCode').text
#                     self.choices_stock_vertical_name = choices_stock_vertical_element.find('choicesStockVerticalName').text
#                     self.choices_stock_vertical_seq = choices_stock_vertical_element.find('choicesStockVerticalSeq').text
#         class ChoicesStock(XMLSerializable):
#             element_name = 'choicesStocks'
#             required_for_add = [
#                 'choices_stock_horizontal_code',
#                 'choices_stock_vertical_code',
#                 'choices_stock_count'
#             ]
#             def __init__(self, choices_stock_element):
#                 if isinstance(choices_stock_element, dict):
#                     self.choices_stock_horizontal_code = choices_stock_element['choices_stock_horizontal_code']
#                     self.choices_stock_vertical_code = choices_stock_element['choices_stock_vertical_code']
#                     self.choices_stock_shipping_day_id = choices_stock_element['choices_stock_shipping_day_id']
#                     self.choices_stock_count = choices_stock_element['choices_stock_count']
                    
#                 elif isinstance(choices_stock_element, ET.Element):
#                     self.choices_stock_horizontal_code = choices_stock_element.find('choicesStockHorizontalCode').text
#                     self.choices_stock_vertical_code = choices_stock_element.find('choicesStockVerticalCode').text
#                     self.choices_stock_count = choices_stock_element.find('choicesStockCount').text
#                     self.choices_stock_shipping_day_id = choices_stock_element.find('choicesStockShippingDayId').text
#                     self.chioces_stock_shipping_day_disp_txt = choices_stock_element.find('choicesStockShippingDayDispTxt').text
        
#         def add_choices_stock(self, value):
#             if not 'choices_stock_horizontals' in vars(self):
#                 self.choices_stock_horizontals = []
#             if not 'choices_stock_verticals' in vars(self):
#                 self.choices_stock_verticals = []
#             if not 'choices_stocks' in vars(self):
#                 self.choices_stocks = []

#             if len([item for item in self.choices_stock_horizontals if item.choices_stock_horizontal_code == value['choices_stock_horizontal']['choices_stock_horizontal_code']]) == 0:
#                 self.choices_stock_horizontals.append(self.ChoicesStockHorizontal(value['choices_stock_horizontal']))
#             if len([item for item in self.choices_stock_verticals if item.choices_stock_vertical_code == value['choices_stock_vertical']['choices_stock_vertical_code']]) == 0:
#                 self.choices_stock_verticals.append(self.ChoicesStockVertical(value['choices_stock_vertical']))
#             self.choices_stocks.append(self.ChoicesStock({
#                 'choices_stock_horizontal_code': value['choices_stock_horizontal']['choices_stock_horizontal_code'],
#                 'choices_stock_vertical_code': value['choices_stock_vertical']['choices_stock_vertical_code'],
#                 'choices_stock_count': value['choices_stock_count'],
#                 'choices_stock_shipping_day_id': value['choices_stock_shipping_day_id']
#             }))
                 
#         def validate_for_add(self, index):
#             if not self.stock_segment:
#                 self.valid = False
#                 self.error = 'stock_segmentは必須です'
#                 return self.valid
#             else:
#                 if self.stock_segment == STOCK_SEGMENT_NO_CHOICE:
#                     self.required_for_add = [
#                         'stock_count',
#                         'display_stock_threshold'
#                     ]
#                     super().validate_for_add(index)
#                     if self.display_stock_segment == DISPLAY_STOCK_SEGMENT_OCCASOINAL:
#                         if not self.display_stock_threshold:
#                             self.valid = False
#                             self.error = 'disply_stock_thresholdは必須です'
#                             return self.valid
#                 elif self.stock_segment == STOCK_SEGMENT_CHOICES:
#                     self.required_for_add = [
#                         'choices_stock_horizontal_item_name',
#                         'choices_stock_horizontals',
#                         'choices_stock_vertical_item_name',
#                         'choices_stock_verticals',
#                         'choices_stocks'
#                     ]
#                     if not super().validate_for_add(index): # required fields check
#                         return self.valid
#                     # duplicate sequence check
#                     choices_stock_horizontal_seq_list = [h.choices_stock_horizontal_seq for h in self.choices_stock_horizontals]
#                     choices_stock_vertical_seq_list = [v.choices_stock_vertical_seq for v in self.choices_stock_verticals]
#                     # if having duplicates
#                     if len(choices_stock_horizontal_seq_list) != len(set(choices_stock_horizontal_seq_list)):
#                         self.valid = False
#                         self.error = 'choices_stock_horizontal_seqが重複しています'
#                         return self.valid
#                     if len(choices_stock_vertical_seq_list) != len(set(choices_stock_vertical_seq_list)):
#                         self.valid = False
#                         self.error = 'choices_stock_vertical_seqが重複しています'
#                         return self.valid

#                     if self.display_choices_stock_segment == DISPLAY_STOCK_SEGMENT_OCCASOINAL:
#                         if not self.display_chioces_stock_threshold:
#                             self.valid = False
#                             self.error = 'disply_choices_stock_thresholdは必須です'
#                             return self.valid
        
#     def create_params(self, shop_id, mode = API_MODE_REGISTER):
#         request = ET.Element('request')
#         shop_id_element = ET.SubElement(request, 'shopId')
#         shop_id_element.text = shop_id
#         item_element = self.serialize(mode = mode)
#         register_stock_element = item_element.find(f'{mode}Stock')
#         if register_stock_element:
#             item_element.remove(register_stock_element)
#             request.append(register_stock_element)
#         request.append(item_element)
#         return ET.tostring(request)
    
# import math
# class ItemSearchResult(object):
#     def __init__(self, response_parsed, limit, page):
#         self.status = response_parsed.find('./result/status').text
#         if self.status != API_STATUS_SUCCESS:
#             self.error = self.Error(response_parsed.find('./result/error')) 
#             self.pagination = self.Pagination(5, page, 110)
#             print('error')          
#         else:
#             result_count = response_parsed.find('./searchResult/resultCount').text
#             max_count = response_parsed.find('./searchResult/maxCount').text
            
#             self.pagination = self.Pagination(limit, page, int(max_count))            
#             self.items = [Item(item) for item in response_parsed.findall('./searchResult/resultItems')]
            
#             self.max_count = max_count
#     class Error(object):
#         def __init__(self, error_element):
#             self.code = error_element.find('code').text
#             self.message = error_element.find('message').text

#     class Pagination(object):
#         max_display_pages = 10
#         def __init__(self, items_per_page, current_page, max_count):
#             self.item_per_page = items_per_page
#             self.current_page = current_page
#             self.max_count = max_count
#             self.total_pages = math.ceil(max_count / items_per_page)
#             self.init_display_list()
#         @property
#         def has_next(self):
#             return self.total_pages > self.current_page
#         @property
#         def has_previous(self):
#             return self.current_page > 1
#         @property
#         def first_index_hidden(self):
#             return (self.display_list[0] != 1) if len(self.display_list) > 0 else False
#         @property
#         def last_index_hidden(self):
#             return (self.display_list[len(self.display_list) - 1] != self.total_pages) if len(self.display_list) > 0 else False
        
#         def init_display_list(self):
#             display_count = self.total_pages if self.total_pages < __class__.max_display_pages else __class__.max_display_pages
            
#             if (display_count - 3) % 2 == 0:
#                 left_offset = int((display_count - 3) / 2)
#                 right_offset = int((display_count - 3) / 2)
#             else:
#                 left_offset = int((display_count - 4) / 2)
#                 right_offset = int((display_count - 2) / 2)
                
#             if (self.current_page - left_offset) < 1:
#                 print('margin')
#                 margin = left_offset - (self.current_page - 1)
#                 print(margin)
#                 left_offset -= margin
#                 right_offset += margin
           
#             self.display_list = [index for index in range(self.current_page - left_offset, self.current_page + right_offset + 1)]

    



