from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
from django.db import connection
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Sync items'
    task_name = 'BASE->データベース 商品同期'
    
    def run(self, user, **options):
        thebase_api = ThebaseApi(user.thebase_auth)
        
        # delete all items
        self.custom_log('テーブル Item のデータを削除します。')
        Item.objects.filter(user = user).delete()

        self.custom_log('テーブル ItemCategory のデータを削除します。')
        ItemCategory.objects.filter(user = user).delete()

        all_items = thebase_api.fetch_all()
        if all_items == False:
            raise Exception(f'処理が異常終了しました。 {thebase_api.error}')
            
        for item_dict in all_items:
            self.custom_log(f'商品:{item_dict["title"]}をデータベースに登録します。')
            item = Item(user = user)
            variations = []
            for key, value in item_dict.items():
                if key == 'variations':
                    for var in item_dict[key]:
                        self.custom_log(f'バリエーション {var["variation"]}をデータベースに登録します。')
                        variation_obj = Variation(item = item)
                        for v_k, v_v in var.items():
                            setattr(variation_obj, v_k, v_v)
                        variations.append(variation_obj)    
                    continue
                if key in vars(item):
                    setattr(item, key, value)
            item.save()
            for var in variations:
                var.save()

            item_categories = thebase_api.get_item_categories(item)
            if item_categories == False:
                raise Exception(f'異常終了しました。{thebase_api.error}')
            item_categories = item_categories['item_categories']
            for item_category in item_categories:
                self.custom_log(f'商品カテゴリ {item_category["item_category_id"]}をデータベースに登録します')
                item_category_obj = ItemCategory(user = user)
                for k,v in item_category.items():
                    setattr(item_category_obj, k, v)
                item_category_obj.save()

            self.custom_log(f'商品:{item_dict["title"]}の処理が完了しました。')