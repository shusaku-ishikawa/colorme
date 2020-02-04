from django.core.management.base import BaseCommand, CommandError
from colorme.models import Item as colorme_Item
from thebase.models import Item as thebase_Item
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Sync with colorme'
    task_name = 'カラーミー->BASE商品同期'

    def run(self, user, **options):
        thebase_api = ThebaseApi(user.thebase_auth)
        for colorme_item in colorme_Item.objects.filter(user = user):
            self.custom_log(f'{colorme_item.item_name}を処理します。')
            try:    
                base_item = thebase_Item.objects.get(identifier = colorme_item.kataban)
            except thebase_Item.DoesNotExist:
                # if new
                try:
                    item = thebase_api.add(colorme_item.base_add_api_params, colorme_item.categories, colorme_item.images)
                except Exception as e:
                    self.custom_log(f'次の理由で登録されませんでした。{str(e)}')
                else:
                    self.custom_log(f'正常に登録されました。')
            else: # if update
                try:
                    item = thebase_api.edit(colorme_item.base_edit_api_params(base_item), colorme_item.categories, colorme_item.images)
                except Exception as e:
                    self.custom_log(f'次の理由で更新されませんでした。{str(e)}')
                else:
                    self.custom_log(f'正常に更新されました。')
