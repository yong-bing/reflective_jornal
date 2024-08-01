from django.http import HttpResponse
from django.shortcuts import render

from blog import models
from blog.utils.captcha import create_captcha


def index(request):
    # 查询所有已发表的文章 status=0
    # articles = models.Article.objects.filter(status=1).order_by('-created_time')

    featured_articles = models.Article.objects.filter(status=1).order_by('-views')[:3]

    latest_articles = models.Article.objects.filter(status=1).order_by('-created_time')[:3]

    categories = models.Category.objects.all()

    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'categories': categories,
    }

    return render(request, 'blog/index.html', context)


def get_captcha(request):
    code = create_captcha(request)
    return HttpResponse(code, content_type='image/png')


def test(request):
    articles = models.Article.objects.filter(status=1).all()
    context = {
        'articles': articles,
    }
    return render(request, 'blog/test.html', context)
