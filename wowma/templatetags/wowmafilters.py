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
    if not vertical_key and horizontal_key:
        return [s.choicesStockCount for s in obj.choicesStocks.all() if s.choicesStockHorizontalCode == horizontal_key][0]
    elif vertical_key and not horizontal_key:
        return [s.choicesStockCount for s in obj.choicesStocks.all() if s.choicesStockVerticalCode == vertical_key][0]
    else:
        return [s.choicesStockCount for s in obj.choicesStocks.all() if s.choicesStockHorizontalCode == horizontal_key and s.choicesStockVerticalCode == vertical_key][0]

@register.filter
def left(value, l):
    return f'{value[:l]}...' 
