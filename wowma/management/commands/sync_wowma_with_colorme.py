from django.core.management.base import BaseCommand, CommandError
from colorme.models import Item as colorme_Item
from wowma.models import Item as wowma_Item
from colorme.enums import *
from django.utils import timezone
from core.models import User
from wowma.wowma_api import WowmaApi
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Sync with colorme'
    task_name = 'カラーミー->Wowma商品同期'

    def run(self, user, **options):
        
        wowma_api = WowmaApi(user.wowma_auth)

        for colorme_item in colorme_Item.objects.filter(user = user):
            self.custom_log(f'{colorme_item.item_name}を処理します。')
            try:    
                wowma_item = wowma_Item.objects.get(itemManagementId = colorme_item.kataban)
            except wowma_Item.DoesNotExist:
                # if new
                try:
                    item = wowma_api.add(colorme_item.wowma_add_api_params(user.wowma_auth.store_id))
                except Exception as e:
                    self.custom_log(f'次の理由で登録されませんでした。{str(e)}')
                else:
                    self.custom_log(f'正常に登録されました。')
                    item = Item(user = self.auth_info.user)
                    item.set_attributes(colorme_item.xml_serialize_item())
                    register_stock = RegisterStock(item = item)
                    register_stock.set_attributes(colorme_item.xml_serialize_stock)
                    
            else: # if update
                pass
                try:
                    item = wowma_api.edit(colorme_item.wowma_edit_api_params(user.wowma_auth.store_id))
                except Exception as e:
                    self.custom_log(f'次の理由で更新されませんでした。{str(e)}')
                else:
                    self.custom_log(f'正常に更新されました。')
