from django.core.management.base import BaseCommand, CommandError
from colorme.models import Item as colorme_Item
from thebase.models import Item as thebase_Item
from colorme.enums import *
from django.utils import timezone
from core.models import User
from wowma.wowma_api import WowmaApi
from core.base_command import MyBaseCommnd

class Command(MyBaseCommnd):
    help = 'Sync with colorme'
    task_name = 'カラーミー->Wowma商品同期'

    def run(self, user, **options):
        
        wowma_api = WowmaApi(user.wowma_auth)

        for colorme_item in colorme_Item.objects.filter(user = user):
            self.custom_log(f'{colorme_item.item_name}を処理します。')
            try:    
                wowma_item = wowma_Item.objects.get(identifier = colorme_item.kataban)
            except wowma_Item.DoesNotExist:
                # if new
                try:
                    item = thebase_api.add(colorme_item.wowma_add_api_params, colorme_item.categories, colorme_item.images)
                except Exception as e:
                    self.custom_log(f'BASE新規登録中にエラーが発生しました。{str(e)}')
                else:
                    self.custom_log(f'正常に登録されました。')
            else: # if update
                try:
                    item = thebase_api.edit(colorme_item.wowma_edit_api_params(base_item), colorme_item.categories, colorme_item.images)
                except Exception as e:
                    self.custom_log(f'BASE更新中にエラーが発生しました。{str(e)}')
                else:
                    self.custom_log(f'正常に更新されました。')
