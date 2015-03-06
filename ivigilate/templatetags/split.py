from django import template
register = template.Library()

@register.filter(name='split')
def split(value, args):
    array = args.split(',')
    return value.split(array[0])[int(array[1])]