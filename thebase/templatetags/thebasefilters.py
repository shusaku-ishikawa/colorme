from django import template
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware

register = template.Library()
@register.filter 
def valid(subj):
    return subj > timezone.now()

@register.filter 
def htmlize(subj):
    return subj.replace('\n', '<br>')

@register.filter 
def todatetime(value):
    return make_aware(datetime.fromtimestamp(value))

@register.filter 
def tax_type(value):
    if value == 1:
        return '標準税率'
    elif value == 2:
        return '軽減税率'


