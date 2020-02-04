from django.core.management.base import BaseCommand, CommandError
from colorme.models import *
from io import TextIOWrapper
import csv 
from colorme.enums import *
from django.utils import timezone
from core.models import User
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'データベース内のカラーミー商品をすべて削除します。'
    task_name = 'データベース内カラーミー商品削除'
    def run(self, user, **options):
        target_items = Item.objects.filter(user = user) 
        for item in target_items:
            item.delete()