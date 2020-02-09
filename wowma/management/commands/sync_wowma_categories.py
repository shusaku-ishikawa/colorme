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
        Category.objects.all().delete()

        try:
            all_categories = wowma_api.fetch_categories()
        except:
            raise Exception(f'次の理由で取得できませんでした。 {wowma_api.error}')
        else:
            for category in all_categories:
                fullpath = category.find("ctgryNameFullpath").text
                category_obj = Category()
                category_obj.set_attributes(category)
                self.custom_log(f'カテゴリ:{fullpath}をデータベースに登録しました。')
                
        