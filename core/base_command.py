from django.core.management.base import BaseCommand, CommandError

from django.utils import timezone
from core.models import User
from django.db import connection
from django.utils import timezone

class MyBaseCommand(BaseCommand):
    help = 'base command'
    task_name = 'task name'
    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
    
    def custom_log(self, content):
        self.stdout.write(f'{timezone.now().strftime("%Y/%m/%d %H:%M:%S")} {content}', ending='<br>')
    
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.custom_log(f'[{options["username"]}]存在しないユーザです')
            return False
        self.custom_log(f'{self.task_name}を開始します。')
        self.run(user, **options)
        self.custom_log(f'{self.task_name}が終了しました。')
