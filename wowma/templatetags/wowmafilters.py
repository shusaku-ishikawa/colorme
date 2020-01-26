from django import template
from ..enums import *

register = template.Library()

@register.filter
def display_sell_method(value):
    return SELL_METHODS.get(value)
@register.filter
def display_sale_status(value):
    return SALE_STATUS.get(value)

@register.filter 
def times(number):
    return range(1, number + 1)

@register.filter 
def isnum(subj):
    return subj.isdigit()

@register.filter 
def stock_by_choice(obj, stock_key):
    (vertical_key, horizontal_key) = stock_key.split('^')
    return [s.choices_stock_count for s in obj.choices_stocks if s.choices_stock_horizontal_code == horizontal_key and s.choices_stock_vertical_code == vertical_key][0]

@register.filter
def left(value, l):
    return f'{value[:l]}...' 
