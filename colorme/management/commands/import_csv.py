from django.core.management.base import BaseCommand, CommandError
from colorme.models import *
from io import TextIOWrapper
import csv 
from colorme.enums import *
from django.utils import timezone
from core.models import User
from core.base_command import MyBaseCommand

class Command(MyBaseCommand):
    help = 'Import uploaded csv'
    task_name = 'CSV取り込み処理'
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-f', '--file', type=int)

    def save_product(self, row, username):
        is_update = False
        try:
            item_instance = Item.objects.get(item_id = row[0])
            is_update = True
        except Item.DoesNotExist:
            item_instance = Item()

        for column_index, column_name in enumerate(PRODUCT_COLUMNS):
            if column_name not in dir(Item):
                continue
            setattr(item_instance, column_name, row[column_index] if row[column_index] != '' else None)
        item_instance.user = User.objects.get(username = username)
        if not item_instance.stock_count:
            item_instance.stock_count = 0
        item_instance.save()
        if is_update:
            self.custom_log(f'{item_instance.item_name}の情報を更新しました。')
        else:
            self.custom_log(f'{item_instance.item_name}をデータベースに登録しました。')
    
    def save_option(self, row):
        try:
            item = Item.objects.get(item_id = row[0])
        except Item.DoesNotExist:
            raise Exception(f'[{row[3]}]ひもづく商品が登録されていません。')
        if row[1] == 'name':
            item.option_1_name = row[2]
            item.option_2_name = row[3]
            item.save()
            return True

        # if item record
        try:
            option_instance = Option.objects.get(option_id = row[4])
            is_update = True
        except Option.DoesNotExist:
            is_update = False
            option_instance = Option()

        for column_index, column_name in enumerate(OPTION_COLUMNS):
            if column_name not in dir(Option):
                continue

            if column_name == 'item_id':
                setattr(option_instance, column_name, item)
            else:
                setattr(option_instance, column_name, row[column_index] if row[column_index] != '' else None)
        
        option_instance.save()
        if is_update:
            self.custom_log(f'{option_instance.option_id}の情報を更新しました。')
        else:
            self.custom_log(f'{option_instance.option_id}をデータベースに登録しました。')
    
    def run(self, user, **options):
        if 'file' in options:
            file_id = options['file']
            target_files = UploadFile.objects.filter(id = file_id)
        else:
            target_files = UploadFile.objects.filter(processed_at = None, user__username = options['username'][0]).order_by('-pk')
        
        if len(target_files) == 0:
            self.custom_log('対象ファイルがありませんでした。')
            return False
        for uploaded_object in target_files:
            self.custom_log(f'{uploaded_object.csv_file.name}を処理します。')
        
            csv_data = csv.reader(TextIOWrapper(uploaded_object.csv_file.file, encoding='cp932'))
            for index, row in enumerate(csv_data):
                if index == 0: #ignore header
                    continue
                if uploaded_object.file_type == FILE_TYPE_PRODUCT:
    
                    try:
                        self.save_product(row, options['username'][0])
                    except Exception as e:
                        self.custom_log(f'エラーが発生しました。 {str(e)}')
                        error_record = UploadFileErrorRecord()
                        error_record.parent_file = uploaded_object
                        error_record.line_number = index + 1
                        error_record.error_message = str(e)
                        error_record.save()
                elif uploaded_object.file_type == FILE_TYPE_OPTION:
                    try:
                        self.save_option(row)
                    except Exception as e:
                        self.custom_log(f'エラーが発生しました。 {str(e)}')
                        error_record = UploadFileErrorRecord()
                        error_record.parent_file = uploaded_object
                        error_record.line_number = index + 1
                        error_record.error_message = str(e)
                        error_record.save()

            uploaded_object.processed_at = timezone.now()
            uploaded_object.save()
