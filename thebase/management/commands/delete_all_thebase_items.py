from django.core.management.base import BaseCommand, CommandError
from thebase.models import *
from io import TextIOWrapper
import csv 
from thebase.enums import *
from django.utils import timezone
from core.models import User
from thebase.thebase_api import ThebaseApi
from django.utils import timezone
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'delete all items for user'
    task_name = 'データベース内およびBASE内のすべての商品削除'
    
    def run(self, user, **options):
        thebase_api = ThebaseApi(user.thebase_auth)
        target_items = Item.objects.filter(user = user) 
        for item in target_items:
            thebase_api.delete(item.item_id)
        