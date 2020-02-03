from django.core.management.base import BaseCommand, CommandError
from colorme.models import *
from io import TextIOWrapper
import csv 
from colorme.enums import *
from django.utils import timezone
from core.models import User

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
        
        target_items = Item.objects.filter(user = user) 
        for item in target_items:
            item.delete()
        self.stdout.write('処理が完了しました。')