from django import template

register = template.Library()

@register.filter
def average(values):
    return sum(values) / len(values) if values else 0
