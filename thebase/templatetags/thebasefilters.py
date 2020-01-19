from django import template
from django.utils import timezone
register = template.Library()
@register.filter 
def valid(subj):
    return subj > timezone.now()

@register.filter 
def htmlize(subj):
    return subj.replace('\n', '<br>')



