from django.core.management.base import BaseCommand, CommandError

from django.utils import timezone
from core.models import User
from django.db import connection
from django.utils import timezone
from colorme.enums import *
from colorme.models import Job
class MyBaseCommand(BaseCommand):
    help = 'base command'
    task_name = 'task name'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs=1, type=str)
        parser.add_argument('-j', '--jobid', type=int)

    def custom_log(self, content):
        self.stdout.write(f'{timezone.now().strftime("%Y/%m/%d %H:%M:%S")} {content}', ending='<br>')
    
    def handle(self, *args, **options):
        if 'jobid' in options and options['jobid']:
            job = Job.objects.get(id = options['jobid'])
        else:
            job = None

        try:
            user = User.objects.get(username = options['username'][0])
        except User.DoesNotExist:
            self.custom_log(f'[{options["username"]}]存在しないユーザです')
            if job:
                job.status = JOB_STATUS_ERROR
                job.save()

            return False

        self.custom_log(f'{self.task_name}を開始します。')
        try:
            self.run(user, **options)
        except Exception as e:
            self.custom_log(f'処理が異常終了しました。{str(e)}')
            if job != None:
                job.status = JOB_STATUS_ERROR
                job.save()
        else:
            self.custom_log(f'{self.task_name}が終了しました。')
            if job != None:
                self.custom_log('hogehoghe')
                job.status = JOB_STATUS_COMPLETED
                job.save()

        