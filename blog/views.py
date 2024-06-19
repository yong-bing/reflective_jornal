from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
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
    article_list = models.Article.objects.all()
    category_list = models.Category.objects.all()

    return render(request, 'blog/index.html',
                  {'article_list': article_list, 'category_list': category_list, 'data_list': []})


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
                avatar = 'avatars/default.png'

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


def blog_post(request, username, article_id):
    article = models.Article.objects.filter(user__username=username, nid=article_id).first()
    context = {
        'username': username,
        'article': article
    }
    return render(request, 'blog/blog_post.html', context)


@login_required
def dashboard(request):
    # 查询当前登录用户的所有文章
    articles = models.Article.objects.filter(user=request.user)
    context = {
        'articles': articles
    }
    return render(request, 'blog/dashboard.html', context)


@login_required
def publish_article(request, nid):
    if request.method == 'POST':
        article = models.Article.objects.filter(nid=nid).first()
        article.description = request.POST.get('description')
        article.state = 1  # 1 表示已发布
        article.save()
        # return JsonResponse({'redirect': True, 'url': 'dashboard'})
        return JsonResponse({'status': 'success', 'message': '文章发布成功'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def test(request):
    return JsonResponse({'status': 'success'})


@login_required
def edit_article(request, nid=None):
    if request.method == 'POST':
        if nid:
            article = get_object_or_404(models.Article, nid=nid, user=request.user)
            create_form = ArticleCreateForm(request.POST, instance=article)
            publish_form = ArticlePublishForm(request.POST, request.FILES, instance=article)
        else:
            create_form = ArticleCreateForm(request.POST)
            publish_form = ArticlePublishForm(request.POST, request.FILES)

        if create_form.is_valid():
            article = create_form.save(commit=False)
            article.user = request.user
            article.state = 0
            article.save()
            if 'save_draft' in request.POST:
                return JsonResponse({'status': 'success', 'message': '已保存为草稿!'})
            elif 'publish' in request.POST:
                # if publish_form.is_valid():
                #     article = publish_form.save(commit=False)
                #     article.state = 1
                #     article.save()
                #     return JsonResponse({'nid': article.nid})
                # else:
                #     return JsonResponse({'errors': publish_form.errors}, status=400)
                return JsonResponse({'nid': article.nid})
        else:
            return JsonResponse({'errors': create_form.errors}, status=400)
    else:
        if nid:
            article = get_object_or_404(models.Article, nid=nid, user=request.user)
            create_form = ArticleCreateForm(instance=article)
            publish_form = ArticlePublishForm(instance=article)
        else:
            article = None
            create_form = ArticleCreateForm()
            publish_form = ArticlePublishForm()
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
    article.delete()
    return JsonResponse({'status': 'success', 'message': 'Article deleted successfully'})


def get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404(f"No {model._meta.object_name} matches the given query.")
