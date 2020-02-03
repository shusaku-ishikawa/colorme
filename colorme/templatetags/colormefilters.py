from django import template
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware

register = template.Library()
@register.filter 
def readable_filetype(value):
    return 'PRODUCT' if value == '0' else 'OPTION'

@register.filter 
def todatetime(value):
    return make_aware(datetime.fromtimestamp(value))
@register.filter 
def extract(value):
    if len(value) > 10:
        print(len(value))
        return f'{value[:10]}...'
    return value

@register.filter 
def tax_type(value):
    if value == 1:
        return '標準税率'
    elif value == 2:
        return '軽減税率'


