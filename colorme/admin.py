from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

# Register your models here.
class UploadFileErrorRecordAdmin(admin.ModelAdmin):
    list_display = ('parent_file', 'error_message', 'line_number')
admin.site.register(UploadFileErrorRecord, UploadFileErrorRecordAdmin)
