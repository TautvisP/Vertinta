from django import template
from modules.orders.enums import MUNICIPALITY_CHOICES, CATEGORY_CHOICES

register = template.Library()

@register.filter
def get_municipality_name(value):
    municipality_dict = dict(MUNICIPALITY_CHOICES)
    return municipality_dict.get(int(value), value)

@register.filter
def translate_category(value):
    return CATEGORY_CHOICES.get(value, value)

@register.filter
def range_filter(value, arg):
    return range(value, arg + 1)

@register.filter(name='in_list')
def in_list(value, arg):
    return value in arg.split(',')