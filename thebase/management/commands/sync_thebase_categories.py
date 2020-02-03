from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi

class Command(BaseCommand):
    help = 'Sync category'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.stdout.write(f'[{options["username"]}]存在しないユーザです', ending="<br>")
            return False
        thebase_api = ThebaseApi(user.thebase_auth)
        categories = thebase_api.get_categories()
        self.stdout.write(f'カテゴリを同期します。', ending="<br>")
        if categories == False:
            self.stdout.write(f'処理が異常終了しました。{thebase_api.error}')
            return
        categories = categories['categories']
        # delete current database
        self.stdout.write('テーブル Category のデータを削除します。', ending="<br>")
        Category.objects.filter(user = user).delete()

        for category in categories:
            self.stdout.write(f'カテゴリ:{category["name"]}をデータベースに登録します。', ending='<br>')
            category_obj = Category(user = user)
            for key, value in category.items():
                if key in vars(category_obj):
                    setattr(category_obj, key, value)
            category_obj.save()
        self.stdout.write('カテゴリの同期が完了しました。', ending="<br>")