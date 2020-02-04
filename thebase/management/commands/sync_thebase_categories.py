from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Sync category'
    task_name = 'BASE->データベース カテゴリ同期'
    
    def run(self, user, **options):

        thebase_api = ThebaseApi(user.thebase_auth)
        categories = thebase_api.get_categories()
        
        if categories == False:
            self.custom_log(f'処理が異常終了しました。{thebase_api.error}')
            return
        categories = categories['categories']
        # delete current database
        self.custom_log('テーブル Category のデータを削除します。')
        Category.objects.filter(user = user).delete()

        for category in categories:
            self.custom_log(f'カテゴリ:{category["name"]}をデータベースに登録します。')
            category_obj = Category(user = user)
            for key, value in category.items():
                if key in vars(category_obj):
                    setattr(category_obj, key, value)
            category_obj.save()
