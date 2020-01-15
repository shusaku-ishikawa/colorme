from django import template
from ..enums import *

register = template.Library()

@register.filter
def display_sell_method(value):
    return SELL_METHODS.get(value)

@register.filter 
def times(number):
    return range(1, number + 1)

@register.filter 
def isnum(subj):
    return subj.isdigit()


