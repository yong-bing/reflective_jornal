from django.contrib import auth
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from blog import models
from blog.blog_forms import UserRegisterForm
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
    user = models.User.objects.filter(username=username).first()
    if not user:
        return render(request, 'blog/404.html')
    # all articles of the user
    articles = user.articles.all()
    # 所有文章的分类及其对应的文章数量
    category_list = models.Category.objects.filter(article2category__article__user=user).annotate(
        num=Count('article2category__article')).order_by('-num')
    context = {
        'user': user,
        'articles': articles,
        'category_list': category_list,
        'article_list': articles,
    }

    return render(request, 'blog/homepage.html', context)


# def test(request):
#     author = {'name': 'alex', 'age': 18, 'bio': 'cool'}
#     categories = [{'name': 'python'}, {'name': 'java'}, {'name': 'c++'}, {'name': 'php'}]
#     post = [
#         {'title': 'python', 'category': 'python', 'content': 'python is good', 'published_date': '2018-01-01'},
#         {'title': 'java', 'category': 'java', 'content': 'java is good', 'published_date': '2018-01-02'},
#         {'title': 'c++', 'category': 'c++', 'content': 'c++ is good', 'published_date': '2018-01-03'},
#         {'title': 'php', 'category': 'php', 'content': 'php is good', 'published_date': '2018-01-04'},
#     ]
#     context = {
#         'author': author,
#         'categories': categories,
#         'page_obj': post
#     }
#     return render(request, 'blog/test.html', context)


def test(request):

    some_markdown_text ="""
# This is a heading

This is some **bold** text and some *italic* text.

- Item 1
- Item 2
- Item 3
"""
    context = {
        'some_markdown_text': some_markdown_text
    }
    return render(request, 'blog/test.html', context)