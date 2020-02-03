from django.core.management.base import BaseCommand, CommandError
from colorme.models import Item as colorme_Item
from thebase.models import Item as thebase_Item
from colorme.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi

class Command(BaseCommand):
    help = 'Sync with colorme'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.stdout.write(f'[{options["username"]}]存在しないユーザです', ending="<br>")
            return False
        thebase_api = ThebaseApi(user.thebase_auth)

        for colorme_item in colorme_Item.objects.filter(user = user):
            self.stdout.write(f'{colorme_item.item_name}を処理します。', ending="<br>")
            try:    
                base_item = thebase_Item.objects.get(identifier = colorme_item.kataban)
            except thebase_Item.DoesNotExist:
                # if new
                #try:
                item = thebase_api.add(colorme_item.base_add_api_params, colorme_item.base_categories, colorme_item.images)
                # except Exception as e:
                #     self.stdout.write(f'BASE新規登録中にエラーが発生しました。{str(e)}', ending="<br>")
                # else:
                #     self.stdout.write(f'BASE新規登録が完了しました。', ending="<br>")
            else: # if update
                #try:
                item = thebase_api.edit(colorme_item.base_edit_api_params(base_item), colorme_item.base_categories, colorme_item.images)
                # except Exception as e:
                #     self.stdout.write(f'BASE更新中にエラーが発生しました。{str(e)}', ending="<br>")
                # else:
                #     self.stdout.write(f'BASE更新が完了しました。', ending="<br>")
        self.stdout.write('処理が完了しました。', ending="<br>")