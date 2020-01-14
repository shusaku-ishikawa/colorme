from django import template
from ..enums import *

register = template.Library()

@register.filter
def display_sell_method(value, arg):
    return SELL_METHODS.get(value)
@register.filter
def remotedirectory(value, arg):
    return value.replace('/app', '')