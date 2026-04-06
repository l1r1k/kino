# kino/templatetags/query_tags.py
from django import template

register = template.Library()

@register.simple_tag
def update_query(querydict, key, value):
    query = querydict.copy()
    query[key] = value
    return '?' + query.urlencode() + '#kinoafishaSection'

@register.simple_tag
def is_soon_leave(today, last_date):
    diff = last_date - today
    return diff <= 2

@register.simple_tag
def is_leave_today(today, last_date):
    diff = last_date - today
    return diff < 1