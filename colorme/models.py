from django.db import models

from .enums import *
from wowma.enums import *
from wowma.models import ShopCategory
from thebase.models import Item as base_Item
import xml.etree.ElementTree as ET
from wowma.wowma_api import WowmaApi
import base64
class Item(models.Model):
    user = models.ForeignKey(
        to = 'core.User',
        on_delete = models.CASCADE,
        related_name = 'colorme_items'
    )
    item_id = models.CharField(
        verbose_name = '商品ID',
        max_length = 100,
        unique = True
    )
    category_1 = models.CharField(
        verbose_name = 'カテゴリ(大)',
        max_length = 100,
        null = True,
        blank = True
    )
    category_2 = models.CharField(
        verbose_name = 'カテゴリ(小)',
        max_length = 100,
        null = True,
        blank = True
    )
    kataban = models.CharField(
        verbose_name = '型番',
        max_length = 100,
        null = True,
        blank = True
    )
    item_name = models.CharField(
        verbose_name = '商品名',
        max_length = 255,
    )
    image_url = models.URLField(
        verbose_name = '商品画像URL',
        max_length = 255,
        null = True,
        blank = True
    )
    create_feature_phone_image = models.CharField(
        verbose_name = 'フィーチャーフォン向け画像作成',
        max_length = 100,
    )
    extra_image_1_url = models.URLField(
        verbose_name = 'その他画像1URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_2_url = models.URLField(
        verbose_name = 'その他画像2URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_3_url = models.URLField(
        verbose_name = 'その他画像3URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_4_url = models.URLField(
        verbose_name = 'その他画像4URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_5_url = models.URLField(
        verbose_name = 'その他画像5URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_6_url = models.URLField(
        verbose_name = 'その他画像6URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_7_url = models.URLField(
        verbose_name = 'その他画像7URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_8_url = models.URLField(
        verbose_name = 'その他画像8URL',
        max_length = 255,
        null = True,
        blank = True
    )
    extra_image_9_url = models.URLField(
        verbose_name = 'その他画像9URL',
        max_length = 255,
        null = True,
        blank = True
    )
    sell_price = models.IntegerField(
        verbose_name = '販売価格',
    )
    member_price = models.IntegerField(
        verbose_name = '会員価格'
    )
    regular_price = models.IntegerField(
        verbose_name = '定価',
        null = True,
        blank = True
    )
    cost_price = models.IntegerField(
        verbose_name = '原価',
        null = True,
        blank = True
    )
    stock_count = models.IntegerField(
        verbose_name = '在庫数',
    )
    manage_stock = models.CharField(
        verbose_name = '在庫管理',
        max_length = 100
    )
    min_purchase_qty = models.IntegerField(
        verbose_name = '最小購入数量',
        null = True,
        blank = True
    )
    max_purchase_qty = models.IntegerField(
        verbose_name = '最大購入数量',
        null = True,
        blank = True
    )
    sale_start_date = models.DateField(
        verbose_name = '販売開始日付',
        null = True,
        blank = True
    )
    sale_start_time = models.TimeField(
        verbose_name = '販売開始時間',
        null = True,
        blank = True
    )
    sale_end_date = models.DateField(
        verbose_name = '販売終了日付',
        null = True,
        blank = True
    )
    sale_end_time = models.TimeField(
        verbose_name = '販売終了時間',
        null = True,
        blank = True
    )
    unit = models.CharField(
        verbose_name = '単位',
        max_length = 100,
        null = True,
        blank = True
    )
    weight = models.FloatField(
        verbose_name = '重量',
        null = True,
        blank = True
    )
    outstock_message = models.CharField(
        verbose_name = '売り切れ時メッセージ',
        max_length = 100,
        null = True,
        blank = True 
    )
    optimal_stock_count = models.IntegerField(
        verbose_name = '適正在庫数',
        null = True,
        blank = True
    )
    display_seq = models.IntegerField(
        verbose_name = '表示順',
        null = True,
        blank = True
    )
    short_description = models.CharField(
        verbose_name = '簡易説明',
        max_length = 255,
        null =True,
        blank = True
    )
    description = models.TextField(
        verbose_name = '商品説明'
    )
    description_for_feature_phone_shop = models.TextField(
        verbose_name = 'フィーチャーフォン向けショップ用商品説明',
        null = True,
        blank = True
    )
    description_for_smartphone_shop = models.TextField(
        verbose_name = 'スマートフォン向けショップ用商品説明',
        null = True,
        blank = True
    )
    use_new_mark = models.CharField(
        verbose_name = 'Newマーク付加設定',
        max_length = 100,
    )
    new_mark_image = models.IntegerField(
        verbose_name = 'Newマーク画像',
        null = True,
        blank = True
    )
    ad_category_id = models.IntegerField(
        verbose_name = '広告用カテゴリID',
        null =True,
        blank = True
    )
    ad_tag_1 = models.CharField(
        verbose_name = '広告用タグ1',
        max_length = 100,
        null = True,
        blank = True
    )
    ad_tag_2 = models.CharField(
        verbose_name = '広告用タグ2',
        max_length = 100,
        null = True,
        blank = True
    )
    ad_tag_3 = models.CharField(
        verbose_name = '広告用タグ3',
        max_length = 100,
        null = True,
        blank = True
    )
    ad_description = models.CharField(
        verbose_name = '広告用商品説明',
        max_length = 255,
        null = True,
        blank = True
    )
    brand = models.CharField(
        verbose_name = 'ブランド',
        max_length = 255,
        null = True,
        blank = True
    )
    jan_isbn = models.CharField(
        verbose_name = 'JAN/ISBN',
        max_length = 100,
        null = True,
        blank = True
    )
    mpn = models.CharField(
        verbose_name = 'MPN',
        max_length = 100,
        null = True,
        blank = True
    )
    condition = models.CharField(
        verbose_name = '状態',
        max_length = 100,
        null = True,
        blank = True
    )
    gender = models.CharField(
        verbose_name = '性別',
        max_length = 100,
        null = True,
        blank = True
    )
    color = models.CharField(
        verbose_name = '色',
        max_length = 100,
        null = True,
        blank = True
    )
    size = models.CharField(
        verbose_name = 'サイズ',
        max_length = 100,
        null = True,
        blank = True
    )
    title = models.CharField(
        verbose_name = 'タイトル',
        max_length = 100,
        null = True,    
        blank = True
    )
    keyword = models.CharField(
        verbose_name = 'キーワード',
        max_length = 100,
        null = True,    
        blank = True
    )
    page_abstract = models.CharField(
        verbose_name = 'ページ概要',
        max_length = 255,
        null = True,
        blank = True
    )
    transfer_fee = models.IntegerField(
        verbose_name = '個別送料',
        null = True,
        blank = True
    )
    display_status = models.CharField(
        verbose_name = '掲載設定',
        max_length = 100
    )
    discount_tax_rate = models.CharField(
        verbose_name = '軽減税率設定',
        max_length = 100
    )
    option_1_name = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    option_2_name = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    @property
    def thebase_item_tax_type(self):
        return 1 if 'しない' in self.discount_tax_rate else 2,
    @property
    def thebase_visible(self):
        return 1 if 'する' in self.display_status else 0
    @property
    def thebase_price(self):
        return self.sell_price - 500 if self.sell_price > 500 else 100
    

    @property
    def wowma_price(self):
        return str(self.sell_price - 300)

    @property
    def wowma_sale_status(self):
        if 'する' in self.display_status:
            return '1' # 販売中
        else:
            return '2' # 販売終了
    @property
    def images(self):
        if not self.image_url:
            return []
        images = [self.image_url]
        images.extend(self.extra_images)
        return images

    @property
    def categories(self):
        return {
            'category_1': self.category_1,
            'category_2': self.category_2
        }
        
    @property
    def extra_images(self):
        return [getattr(self, f'extra_image_{i}_url') for i in range(1, 10) if getattr(self, f'extra_image_{i}_url')]
    
    @property
    def custom_description(self):
        body = self.description
        body += '<br>'
        for image in self.images:
            body += f'<img src="{image}" alt="{self.item_name}"><br>'
        body += r'<center><div id="banner_body" style="width:100%;max-width:760px;margin-top:0;margin-bottom:0;margin-right:auto;margin-left:auto;"><div id="banner_wrapper_item" style="font-size:0;"><a href="/user/43778737/list/?categ_id=5108" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/tops.jpg"></a><a href="/user/43778737/list/?categ_id=510811" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/knit.jpg"></a><a href="/user/43778737/list/?categ_id=5103" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/outer.jpg"></a><a href="/user/43778737/list/?categ_id=5110" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/bottoms.jpg"></a><a href="/user/43778737/list/?categ_id=5111" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/onepiece.jpg"></a><a href="/user/43778737/list/?categ_id=5109" style="display:inline-block;width:97%;margin-top:0;margin-bottom:5px;margin-right:1%;margin-left:1%;"><img width="100%" src="https://image.wowma.jp/43778737/shop/dress.jpg"></a></div></div></center>'
        return body

    @property   
    def base_add_api_params(self):
        params = {
            'title': f'{self.item_name} {self.kataban if self.kataban else ""}'.strip(),
            'detail': self.custom_description,
            'price': self.thebase_price,
            'item_tax_type': self.thebase_item_tax_type,
            'stock': self.stock_count,
            'visible': self.thebase_visible,
            'identifier': self.kataban,
            'list_order': self.display_seq
        }
        for index, var in enumerate(self.options.all()):
            params[f'variation[{index}]'] = var.option_value
            params[f'variation_identifier[{index}]'] = var.option_id
            params[f'variation_stock[{index}]'] = var.stock_count
        return params
    
    @property
    def wowma_cateogry_id(self):
        return '2903' # for test

    def xml_serialize_item(self, mode, lotNumber = None):
        register_item = ET.Element(f'{mode}Item')
        if mode in [API_MODE_UPDATE, API_MDOE_DELETE]:
            lot = ET.SubElement(register_item, 'lotNumber')
            lot.text = lotNumber
        item_name = ET.SubElement(register_item, 'itemName')
        item_name.text = f"送料無料 {self.item_name}"
        item_management_id = ET.SubElement(register_item, 'itemManagementId')
        item_management_id.text = self.kataban
        item_management_name = ET.SubElement(register_item, 'itemManagementName')
        item_management_name.text = self.kataban
        item_code = ET.SubElement(register_item, 'itemCode')
        item_code.text = self.kataban
        item_price = ET.SubElement(register_item, 'itemPrice')
        item_price.text = self.wowma_price
        sell_method_segment = ET.SubElement(register_item, 'sellMethodSegment')
        sell_method_segment.text = '1' # 通常
        tax_segment = ET.SubElement(register_item, 'taxSegment')
        tax_segment.text = '1'
        postage_segment = ET.SubElement(register_item, 'postageSegment')
        postage_segment.text = '2' # 送料込み
        description = ET.SubElement(register_item, 'description')
        description.text = '<br>' #self.custom_description
        description_for_sp = ET.SubElement(register_item, 'descriptionForSP')
        description_for_sp.text = self.custom_description
        description_for_pc = ET.SubElement(register_item, 'descriptionForPC')
        description_for_pc.text = self.custom_description
        
        for index, image_url_text in enumerate(self.images):
            image_root = ET.Element('images')
            image_url = ET.SubElement(image_root, 'imageUrl')
            image_url.text = image_url_text
            image_name = ET.SubElement(image_root, 'imageName')
            image_name.text = f'{self.kataban}_{index + 1}'
            image_seq = ET.SubElement(image_root, 'imageSeq')
            image_seq.text = str(index + 1)
            register_item.append(image_root)

        category_id = ET.SubElement(register_item, 'categoryId')
        category_id.text = self.wowma_cateogry_id
        sale_status = ET.SubElement(register_item, 'saleStatus')
        sale_status.text = self.wowma_sale_status
        return register_item

    def _b64encode(self, target):
        return base64.b64encode(target.encode('utf-8')).decode('ascii').replace('=', "")

    def xml_serialize_stock(self, mode = API_MODE_REGISTER):
        register_stock = ET.Element(f'{mode}Stock')
        stock_segment = ET.SubElement(register_stock, 'stockSegment')
        if self.options.all():
            stock_segment.text = '2'
            stock_count = ET.SubElement(register_stock, 'stockCount')
            stock_count.text = str(self.stock_count)
        else:
            stock_segment.text = '1'
        
        vertical_choice_name = ET.SubElement(register_stock, 'choicesStockVerticalItemName')
        vertical_choice_name.text = self.option_1_name
        vertical_choice_value_list = [op.option_1_value for op in self.options.all()]
        vertical_choice_value_list_no_dups = list(dict.fromkeys(vertical_choice_value_list))

        for index, vertical_choice_value in enumerate(vertical_choice_value_list_no_dups):
            groupelem = ET.SubElement(register_stock, 'choicesStockVerticals')
            code = ET.SubElement(groupelem, 'choicesStockVerticalCode')
            code.text = self._b64encode(vertical_choice_value)
            name = ET.SubElement(groupelem, 'choicesStockVerticalName')
            name.text = vertical_choice_value
            seq = ET.SubElement(groupelem, 'choicesStockVerticalSeq')
            seq.text = str(index + 1)

        horizontal_item_name = ET.SubElement(register_stock, 'choicesStockHorizontalItemName')
        horizontal_item_name.text = self.option_2_name
        horizontal_choice_value_list = [op.option_2_value for op in self.options.all()]
        horizontal_choice_value_list_no_dups = list(dict.fromkeys(horizontal_choice_value_list))
        if not (horizontal_choice_value_list_no_dups[0] == None):
            for index, horizontal_choice_value in enumerate(horizontal_choice_value_list_no_dups):
                groupelem = ET.SubElement(register_stock, 'choicesStockHorizontals')
                code = ET.SubElement(groupelem, 'choicesStockHorizontalCode')
                code.text = self._b64encode(horizontal_choice_value)
                name = ET.SubElement(groupelem, 'choicesStockHorizontalName')
                name.text = horizontal_choice_value
                seq = ET.SubElement(groupelem, 'choicesStockHorizontalSeq')
                seq.text = str(index + 1)
        
        for op in self.options.all():
            groupelem = ET.SubElement(register_stock, 'choicesStocks')
            verticalcode = ET.SubElement(groupelem, 'choicesStockVerticalCode')
            verticalcode.text = self._b64encode(op.option_1_value)
            if op.option_2_value:
                horizontalcode = ET.SubElement(groupelem, 'choicesStockHorizontalCode')
                horizontalcode.text = self._b64encode(op.option_2_value)
            choicesstockcount = ET.SubElement(groupelem, 'choicesStockCount')
            choicesstockcount.text = str(op.stock_count)
        return register_stock

    def wowma_api_params(self, shopId, mode, lotNumber = None):
        request = ET.Element('request')
        shopid = ET.SubElement(request, 'shopId')
        shopid.text = shopId
        register_item = self.xml_serialize_item(mode, lotNumber=lotNumber)
        register_stock = self.xml_serialize_stock(mode)
        request.append(register_item)
        request.append(register_stock)
        print(ET.tostring(request))
        return ET.tostring(request)

    def base_edit_api_params(self, base_item):
        params = self.base_add_api_params
        params['item_id'] = base_item.item_id
        for index, op in enumerate(self.options.all()):
            exists = [var.variation_id for var in base_item.variations.all() if var.variation_identifier == op.option_id]
            if len(exists) == 0: # if new then no varition id
                pass
            elif len(exists) == 1: # if already exist then set variation_id
                params[f'variation_id[{index}]'] = exists[0]
        return params
    


class Option(models.Model):
    item_id = models.ForeignKey(
        to = Item,
        related_name = 'options',
        on_delete = models.CASCADE
    )
    option_1_value = models.CharField(
        max_length = 100
    )
    option_2_value = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    option_id = models.CharField(
        max_length = 100
    )
    kataban = models.CharField(
        max_length = 100,
        null = True,
        blank = True
    )
    stock_count = models.IntegerField(
        null = True,
        blank = True,
    )
    optimal_stock_count = models.IntegerField(
        null = True,
        blank = True
    )
    sale_price = models.IntegerField(
        null = True,
        blank = True
    )
    member_price = models.IntegerField(
        null = True,
        blank = True
    )
    @property
    def option_value(self):
        
        return f'{self.option_1_value}{self.option_2_value if self.option_2_value else ""}'


# Create your models here.
class UploadFile(models.Model):
    user = models.ForeignKey(
        to = 'core.User',
        on_delete = models.CASCADE,
        related_name = 'uploaded_files'
    )
    csv_file = models.FileField(
        verbose_name = 'product.csv',
        upload_to = 'uploaded'
    )
    file_type = models.CharField(
        max_length = 100,
        choices = (
            (FILE_TYPE_PRODUCT, 'product.csv'),
            (FILE_TYPE_OPTION, 'optino.csv')
        )
    )
   
    uploaded_at = models.DateTimeField(
        verbose_name = '登録日',
        auto_now_add = True
    )
    processed_at = models.DateTimeField(
        verbose_name = '処理日',
        null = True,
        blank = True
    )
class UploadFileErrorRecord(models.Model):
    parent_file = models.ForeignKey(
        verbose_name = '親ファイル',
        to = UploadFile,
        related_name = 'errors',
        on_delete = models.CASCADE
    )
    line_number = models.IntegerField(
        verbose_name = '行番号',
    )
    error_message = models.CharField(
        verbose_name = 'エラー',
        null = True,
        blank = True,
        max_length = 255
    )

class Job(models.Model):
    
    user = models.ForeignKey(
        to = 'core.User',
        on_delete = models.CASCADE
    )
    job_name = models.CharField(
        max_length = 255,
        choices = (
            ('import_csv', 'CSV取り込み'),
            ('sync_thebase', 'BASEへ反映'),
            ('sync_wowma', 'WOWMAへ反映')
        )
    )
    registered_at = models.DateTimeField(
        auto_now_add = True
    )
    status = models.CharField(
        max_length = 100,
        default = JOB_STATUS_WAITING
    )
    completed_at = models.DateTimeField(
        null = True,
        blank = True
    )
    log = models.TextField(
        null = True
    )
    @property
    def status_readable(self):
        return JOB_STATUS_MESSAGES[self.status]
