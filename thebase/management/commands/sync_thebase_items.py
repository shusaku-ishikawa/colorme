from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
from django.db import connection

class Command(BaseCommand):
    help = 'Sync items'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.stdout.write(f'[{options["username"]}]存在しないユーザです', ending="<br>")
            return False

        thebase_api = ThebaseApi(user.thebase_auth)
        
        # delete all items
        self.stdout.write('テーブル Item のデータを削除します。', ending="<br>")
        Item.objects.filter(user = user).delete()

        self.stdout.write('テーブル ItemCategory のデータを削除します。', ending="<br>")
        ItemCategory.objects.filter(user = user).delete()

        all_items = thebase_api.fetch_all()
        if all_items == False:
            self.stdout.write(f'処理が異常終了しました。 {thebase_api.error}', ending="<br>")
            return False
        for item_dict in all_items:
            self.stdout.write(f'商品:{item_dict["title"]}をデータベースに登録します。', ending='<br>')
            item = Item(user = user)
            variations = []
            for key, value in item_dict.items():
                if key == 'variations':
                    for var in item_dict[key]:
                        self.stdout.write(f'バリエーション {var["variation"]}をデータベースに登録します。', ending='<br>')
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
                self.stdout.write(f'異常終了しました。{thebase_api.error}', ending='<br>')
                return
            item_categories = item_categories['item_categories']
            for item_category in item_categories:
                self.stdout.write(f'商品カテゴリ {item_category["item_category_id"]}をデータベースに登録します', ending="<br>")
                item_category_obj = ItemCategory(user = user)
                for k,v in item_category.items():
                    setattr(item_category_obj, k, v)
                item_category_obj.save()

            self.stdout.write(f'商品:{item_dict["title"]}の処理が完了しました。', ending="<br>")
        
        
        self.stdout.write('データベースの同期処理が完了しました。', ending="<br>")