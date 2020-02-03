from background_task import background
from django.core.management import call_command
from .models import Job
from .enums import *
from io import StringIO
from django.utils import timezone
@background(schedule=5)
def execute_job_by_user(job_id):
    job = Job.objects.get(id = job_id)
    print(job_id)
    job.status = JOB_STATUS_IN_PROGRESS
    job.save()

    outstream = StringIO()
    call_command(job.job_name, job.user.username, stdout = outstream)
    outstream.seek(0)
    job.log = outstream.read()
    
    job.status = JOB_STATUS_COMPLETED
    job.completed_at = timezone.now()
    job.save()
