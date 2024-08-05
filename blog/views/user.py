from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from blog import models


def homepage(request, username):
    articles = models.Article.objects.filter(author__username=username, status=1)
    context = {
        'username': username,
        'articles': articles
    }
    return render(request, 'blog/homepage.html', context)


@login_required
def dashboard(request):
    articles = models.Article.objects.filter(author=request.user)
    draft_count = articles.filter(status=0).count()
    published_count = articles.filter(status=1).count()
    context = {
        'articles': articles,
        'draft_count': draft_count,
        'published_count': published_count
    }
    return render(request, 'blog/dashboard.html', context)
