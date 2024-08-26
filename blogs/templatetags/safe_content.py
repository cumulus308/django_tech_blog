from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

@register.filter(name='safe_content')
def safe_content(value):
    allowed_tags = ['p', 'br']
    cleaned_content = bleach.clean(value, tags=allowed_tags, strip=True)
    return mark_safe(cleaned_content)