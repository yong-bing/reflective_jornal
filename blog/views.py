import os
import re

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from blog import models
from blog.blog_forms import UserRegisterForm, ArticleCreateForm, ArticlePublishForm
from blog.utils import verification_code


# Create your views here.


def login(request):
    if request.method == 'POST':
        response = {'username': None, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        verification = request.POST.get('verification_code')
        if verification.upper() == request.session.get('verification_code').upper():
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                response['username'] = user.username
            else:
                response['msg'] = '用户名或密码错误！'
        else:
            response['msg'] = '验证码错误！'
        return JsonResponse(response)

    return render(request, 'blog/login.html')


def logout(request):
    auth.logout(request)  # request.session.flush()
    return redirect(index)


def index(request):
    articles = models.Article.objects.all().order_by('-created_time')
    categories = models.Category.objects.all()

    context = {
        'articles': articles,
        'categories': categories,
    }

    return render(request, 'blog/index.html', context)


def register(request):
    if request.method == 'POST':
        response = {'username': None, 'msg': ''}
        user_form = UserRegisterForm(request.POST, request.FILES)
        if user_form.is_valid():
            response['username'] = user_form.cleaned_data.get('username')

            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            email = user_form.cleaned_data.get('email')
            avatar = user_form.cleaned_data.get('avatar')
            if avatar is None:
                avatar = 'avatars/default.jpg'

            models.Homepage.objects.create(title=username, url=username)
            models.User.objects.create_user(username=username, password=password, email=email, avatar=avatar)

        else:
            response['msg'] = user_form.errors
        return JsonResponse(response)

    return render(request, 'blog/register.html', {'form': UserRegisterForm()})


def get_verification_code(request):
    code = verification_code.create_code(request)
    return HttpResponse(code, content_type='image/png')


# 个人站点主页
def homepage(request, username):
    # 查询用户对应下的所有文章
    articles = models.Article.objects.filter(user__username=username)
    context = {
        'username': username,
        'articles': articles
    }
    return render(request, 'blog/homepage.html', context)


def article_detail(request, username, article_id):
    article = models.Article.objects.filter(user__username=username, nid=article_id).first()
    if article:
        article.views += 1
        article.save()
    context = {
        'username': username,
        'article': article
    }
    return render(request, 'blog/article_detail.html', context)


@login_required
def dashboard(request):
    # 查询当前登录用户的所有文章
    articles = models.Article.objects.filter(user=request.user)
    # 统计其中的草稿数量和已发布数量
    draft_count = articles.filter(status=0).count()
    published_count = articles.filter(status=1).count()
    context = {
        'articles': articles,
        'draft_count': draft_count,
        'published_count': published_count
    }
    return render(request, 'blog/dashboard.html', context)


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


def test(request):
    return render(request, 'blog/test.html')


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
        create_form = ArticleCreateForm(instance=article, user=request.user)
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
    article = get_object_or_404(models.Article, nid=nid, user=request.user)
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


def get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404("找不到指定的对象")
