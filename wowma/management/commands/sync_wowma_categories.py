from django.core.management.base import BaseCommand, CommandError
from wowma.models import *
from django.utils import timezone
from core.models import User
from wowma.wowma_api import WowmaApi
from django.db import connection
from django.utils import timezone
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Sync wowma categories '
    task_name = 'Wowmaカテゴリ同期'

    def run(self, user, **options):
    
        wowma_api = WowmaApi(user.wowma_auth)    
        # delete all items
        self.custom_log('テーブル Cateogry のデータを削除します。')
        Cateogry.objects.filter(user = user).delete()

        try:
            all_categories = wowma_api.fetch_all_categoeis()
        except:
            self.custom_log(f'処理が異常終了しました。 {wowma_api.error}')
            return False
        else:
            for item_element in all_items:
                category_name = item_element.find("shopCategoryName").text
                item = Item(user = user)
                item.set_attributes(item_element)
                self.custom_log(f'カテゴリ:{category_name}をデータベースに登録しました。')
                
        