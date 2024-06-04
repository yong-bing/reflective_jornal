from django import template

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
