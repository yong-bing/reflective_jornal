from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

from blog import models
from blog.utils.captcha import create_captcha


def get_captcha(request):
    code = create_captcha(request)
    return HttpResponse(code, content_type='image/png')


def get_articles_by_category(request):
    category_id = request.GET.get("category", "all")
    page_number = request.GET.get("page", 1)
    search = request.GET.get("search", "")

    # 基础查询
    articles = models.Article.objects.filter(status=1).order_by("-created_time")

    # 分类筛选
    if category_id != "all":
        articles = articles.filter(categories__nid=category_id)

    # 搜索筛选，Q对象模糊查询
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(desc__icontains=search))

    articles = articles.order_by("-created_time")
    paginator = Paginator(articles, 6)
    page_obj = paginator.get_page(page_number)

    article_list = [
        {
            "nid": article.nid,
            "title": article.title,
            "desc": article.desc,
            "cover": article.cover.url,
            "author": article.author.username,
            "created_time": article.created_time.strftime("%Y年%m月%d日"),
            "views": article.views,
            "url": f"/{article.author.username}/articles/{article.nid}",
            "tags": [tag.content for tag in article.tags.all()],
            "read_time": "3分钟",
        }
        for article in page_obj.object_list
    ]

    data = {
        "page_articles": article_list,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
    }

    return JsonResponse(data)
