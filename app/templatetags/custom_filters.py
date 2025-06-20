from django import template
from bson import ObjectId

register = template.Library()

@register.filter
def to_objectid(value):
    try:
        return ObjectId(value)
    except:
        return None