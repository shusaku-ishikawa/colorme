from django.core.management.base import BaseCommand, CommandError
from wowma.models import *
import csv 
from wowma.enums import *
from django.utils import timezone
from core.models import User
from wowma.wowma_api import WowmaApi
from django.utils import timezone
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'delete all items for user'
    task_name = 'データベース内およびWowma内のすべての商品削除'
    
    def run(self, user, **options):
        wowma_api = WowmaApi(user.wowma_auth)
        target_items = Item.objects.filter(user = user) 
        for item in target_items:
            wowma_api.delete_item(item.id)
        