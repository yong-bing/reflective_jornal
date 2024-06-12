from django import template
from django.db.models import Count

from blog import models

register = template.Library()


@register.filter(name='batch')
def batch(iterable, n=3):
    batch_list = []
    for i in range(0, len(iterable), 1):
        if i < len(iterable) - n:
            batch_list.append(iterable[i:i + n])
        else:
            batch_list.append(iterable[i:] + iterable[:n - (len(iterable) - i)])
    return batch_list


@register.inclusion_tag('blog/components/sidebar_personal.html')
def sidebar_personal(username):
    user = models.User.objects.filter(username=username).first()
    category_list = models.Category.objects.filter(article2category__article__user=user).annotate(
        num=Count('article2category__article')).order_by('-num')
    context = {
        'user': user,
        'category_list': category_list,
    }

    return context
