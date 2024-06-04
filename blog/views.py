from django.contrib import auth
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
    data_list = [
        {'title': 'Card 1', 'text': 'This is the first card.'},
        {'title': 'Card 2', 'text': 'This is the second card.'},
        {'title': 'Card 3', 'text': 'This is the third card.'},
        {'title': 'Card 4', 'text': 'This is the fourth card.'},

    ]
    article_list = models.Article.objects.all()
    # category_list = models.Category.objects.all()
    category_list = ["测试1", "测试2", "测试3", "测试4", "测试5", "测试6", "测试7", "测试8", "测试9", "测试10",] * 2
    return render(request, 'blog/index.html',
                  {'article_list': article_list, 'category_list': category_list, 'data_list': data_list})


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

            models.UserInfo.objects.create_user(username=username, password=password, email=email, avatar=avatar)

        else:
            response['msg'] = user_form.errors
        return JsonResponse(response)

    return render(request, 'blog/register.html', {'form': UserRegisterForm()})


def get_verification_code(request):
    code = verification_code.create_code(request)
    return HttpResponse(code, content_type='image/png')


# 个人站点主页
def home_site(request, username):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'blog/404.html')
    return render(request, 'blog/404.html', {'user': user})


def test(request):
    data_list = [
        {'title': 'Card 1', 'text': 'This is the first card.'},
        {'title': 'Card 2', 'text': 'This is the second card.'},
        {'title': 'Card 3', 'text': 'This is the third card.'}
    ]
    return render(request, 'blog/test.html', {'data_list': data_list})
