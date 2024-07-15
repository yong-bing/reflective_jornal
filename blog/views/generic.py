from django.http import HttpResponse
from django.shortcuts import render

from blog import models
from blog.utils.captcha import create_captcha


def index(request):
    # 查询所有已发表的文章 status=0
    articles = models.Article.objects.filter(status=1).order_by('-created_time')

    # articles = models.Article.objects.all().order_by('-created_time')
    categories = models.Category.objects.all()

    context = {
        'articles': articles,
        'categories': categories,
    }

    return render(request, 'blog/index.html', context)


def get_captcha(request):
    code = create_captcha(request)
    return HttpResponse(code, content_type='image/png')


def test(request):
    print(request.get_host())
    return render(request, 'blog/article-admin.html',)