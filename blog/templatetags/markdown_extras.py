import markdown2
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    print("Rendering Markdown: ", text)
    html = mark_safe(markdown2.markdown(text))
    print("Rendered HTML: ", html)
    return html
