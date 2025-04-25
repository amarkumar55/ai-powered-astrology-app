from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(str(key), "")


@register.filter(name='replace')
def replace(string, arg):
    """
    Replaces the first part of the argument with the second part.
    Usage: {{ value|replace:"_,-" }}
    """
    try:
        key, replace_by = arg.split(',')
        return string.replace(key, replace_by)
    except ValueError:
        return string
    
@register.filter
def dict_get(dict_obj, key):
    return dict_obj.get(key, {})


@register.filter
def to_int(value):
    return int(value)