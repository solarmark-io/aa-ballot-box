from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter(name='render_markdown')
def render_markdown(text):
    if not text:
        return ""
    
    # 'extra' allows tables and formatting, 'nl2br' respects single line breaks
    rendered_html = markdown.markdown(text, extensions=['extra', 'nl2br'])
    return mark_safe(rendered_html)