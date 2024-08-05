import os
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from blog import models
from blog.blog_forms import ArticleCreateForm, ArticlePublishForm


def article_detail(request, username, article_id):
    article = models.Article.objects.filter(author__username=username, nid=article_id).first()
    if article:
        article.views += 1
        article.save()
    context = {"username": username, "article": article}
    return render(request, "blog/article_detail.html", context)


@login_required
def publish_article(request, article_id):
    if request.method == "POST":
        article = models.Article.objects.filter(nid=article_id).first()
        publish_form = ArticlePublishForm(request.POST, request.FILES, instance=article)
        if publish_form.is_valid():
            publish_form.save()
            return JsonResponse({"status": "success", "message": "文章发布成功"})
        else:
            return JsonResponse({"errors": publish_form.errors}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def edit_article(request, article_id=None):
    article = None

    all_categories = models.Category.objects.all()
    all_tags = models.Tag.objects.all()

    if article_id:
        article = get_object_or_404(models.Article, nid=article_id, author=request.user)
    if request.method == "POST":
        create_form = ArticleCreateForm(request.POST, instance=article, author=request.user)
        publish_form = ArticlePublishForm(request.POST, request.FILES, instance=article)

        if create_form.is_valid():
            article = create_form.save()
            if "save_draft" in request.POST:
                return JsonResponse({"status": "success", "message": "已保存为草稿!"})
            elif "publish" in request.POST:
                return JsonResponse({"nid": article.nid})
        else:
            return JsonResponse({"errors": create_form.errors}, status=400)
    else:
        create_form = ArticleCreateForm(instance=article, author=request.user)
        publish_form = ArticlePublishForm(instance=article)

    context = {
        "create_form": create_form,
        "publish_form": publish_form,
        "article": article,
        "all_categories": [cat.content for cat in all_categories],
        "all_tags": [tag.content for tag in all_tags],
    }

    return render(request, "blog/edit.html", context)


@login_required
@require_POST
def delete_article(request, article_id):
    article = get_object_or_404(models.Article, nid=article_id, author=request.user)
    if article.cover.name != "covers/default.jpg":
        cover_path = "." + article.cover.url
        try:
            os.remove(cover_path)
        except FileNotFoundError:
            pass
    img_urls = re.findall(r"!\[.*?]\((.*?)\)", article.content)
    for img_url in img_urls:
        img_url = "." + img_url.replace("\\", "/")
        try:
            os.remove(img_url)
        except FileNotFoundError:
            pass
    article.delete()
    messages.success(request, "文章删除成功")
    return JsonResponse({"status": "success", "message": "文章删除成功"})


def category(request):
    categories = models.Category.objects.all()
    return render(request, "blog/category.html", {"categories": categories})

