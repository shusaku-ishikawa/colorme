from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from io import TextIOWrapper
import csv 
from thebase.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
class Command(BaseCommand):
    help = 'delete all items for user'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
    
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.stdout.write(f'[{options["username"][0]}]存在しないユーザです。')
            return
        thebase_api = ThebaseApi(user.thebase_auth)
        target_items = Item.objects.filter(user = user) 
        for item in target_items:
            thebase_api.delete(item.item_id)
        self.stdout.write('処理が完了しました。')