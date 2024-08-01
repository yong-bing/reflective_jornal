import os
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from blog import models
from blog.blog_forms import ArticleCreateForm, ArticlePublishForm
from blog.views.user import dashboard


def article_detail(request, username, article_id):
    article = models.Article.objects.filter(author__username=username, nid=article_id).first()
    if article:
        article.views += 1
        article.save()
    context = {
        'username': username,
        'article': article
    }
    return render(request, 'blog/article_detail.html', context)


@login_required
def publish_article(request, nid):
    if request.method == 'POST':
        article = models.Article.objects.filter(nid=nid).first()
        publish_form = ArticlePublishForm(request.POST, request.FILES, instance=article)
        if publish_form.is_valid():
            publish_form.save()
            return JsonResponse({'status': 'success', 'message': '文章发布成功'})
        else:
            return JsonResponse({'errors': publish_form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def edit_article(request, nid=None):
    article = None

    if nid:
        article = get_object_or_404(models.Article, nid=nid, user=request.user)

    if request.method == 'POST':
        create_form = ArticleCreateForm(request.POST, instance=article, user=request.user)
        publish_form = ArticlePublishForm(request.POST, request.FILES, instance=article)

        if create_form.is_valid():
            article = create_form.save()
            if 'save_draft' in request.POST:
                return JsonResponse({'status': 'success', 'message': '已保存为草稿!'})
            elif 'publish' in request.POST:
                return JsonResponse({'nid': article.nid})
        else:
            return JsonResponse({'errors': create_form.errors}, status=400)
    else:
        create_form = ArticleCreateForm(instance=article, author=request.user)
        publish_form = ArticlePublishForm(instance=article)

    context = {
        'create_form': create_form,
        'publish_form': publish_form,
        'article': article
    }

    return render(request, 'blog/edit.html', context)


@login_required
@require_POST
def delete_article(request, nid):
    article = get_object_or_404(models.Article, nid=nid, author=request.user)
    if article.cover.name != 'covers/default.jpg':
        cover_path = "." + article.cover.url
        try:
            os.remove(cover_path)
        except FileNotFoundError:
            pass
    img_urls = re.findall(r'!\[.*?]\((.*?)\)', article.content)
    for img_url in img_urls:
        img_url = "." + img_url.replace('\\', '/')
        try:
            os.remove(img_url)
        except FileNotFoundError:
            pass
    article.delete()
    messages.success(request, '文章删除成功')
    # return JsonResponse({'status': 'success', 'message': '文章删除成功'})
    return redirect(dashboard)


def category(request):
    categories = models.Category.objects.all()
    return render(request, 'blog/category.html', {'categories': categories})


def get_articles_by_category(request):
    category_id = request.GET.get('category', 'all')
    page_number = request.GET.get('page', 1)
    search = request.GET.get('search', '')

    # 基础查询
    articles = models.Article.objects.filter(status=1).order_by('-created_time')

    # 分类筛选
    if category_id != 'all':
        articles = articles.filter(categories__nid=category_id)

    # 搜索筛选，Q对象模糊查询
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(desc__icontains=search))

    articles = articles.order_by('-created_time')
    paginator = Paginator(articles, 6)
    page_obj = paginator.get_page(page_number)

    article_list = [{
        'nid': article.nid,
        'title': article.title,
        'desc': article.desc,
        'cover': article.cover.url,
        'author': article.author.username,
        'created_time': article.created_time.strftime('%Y年%m月%d日'),
        'views': article.views,
        'url': f'/{article.author.username}/articles/{article.nid}',
        'tags': [tag.content for tag in article.tags.all()],
        'read_time': '3分钟'
    } for article in page_obj.object_list]

    data = {
        'page_articles': article_list,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }

    return JsonResponse(data)
