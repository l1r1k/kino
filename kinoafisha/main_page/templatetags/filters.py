from django import template

register = template.Library()

@register.filter
def is_last_day(movie, selected_date):
    return movie.rental_end == selected_date['date_obj']

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)