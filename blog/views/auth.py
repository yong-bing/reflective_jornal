from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from blog import models
from blog.blog_forms import UserRegisterForm, UserLoginForm
from blog.utils.captcha import verify_captcha
from blog.views.generic import index


@ensure_csrf_cookie
def login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        captcha = request.POST.get('captcha')

        if not verify_captcha(request, captcha):
            return JsonResponse({'success': False, 'errors': {'captcha': '验证码错误！'}})

        username = login_form.data.get('username')
        password = login_form.data.get('password')
        remember_me = request.POST.get('remember_me') == 'on'

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': {'auth': '用户名或密码错误！'}})

    return render(request, 'blog/auth/login.html', {'form': UserLoginForm()})


def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        captcha = request.POST.get('captcha')
        if not verify_captcha(request, captcha):
            return JsonResponse({'success': False, 'errors': {'captcha': '验证码错误！'}})
        if user_form.is_valid():
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            email = user_form.cleaned_data.get('email')

            models.Homepage.objects.create(title=username, url=username)
            models.User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'success': True, 'errors': {}})
        else:
            errors = user_form.errors
        return JsonResponse({'success': False, 'errors': errors})

    return render(request, 'blog/auth/register.html', {'form': UserRegisterForm()})


def logout(request):
    auth.logout(request)  # request.session.flush()
    return redirect(index)


@require_http_methods(["GET", "POST"])
@ratelimit(key='ip', rate='5/m', block=True)
def reset_password(request):
    if request.method == 'POST':
        return handle_reset_password_request(request)
    return render(request, 'blog/auth/reset_password.html')


def handle_reset_password_request(request):
    email = request.POST.get('email')
    captcha = request.POST.get('captcha')

    if not verify_captcha(request, captcha):
        return JsonResponse({'success': False, 'errors': {'captcha': '验证码错误！'}})

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'errors': {'email': '请输入有效的邮箱地址。'}})

    user = models.User.objects.filter(email=email).first()
    if user:
        try:
            send_reset_password_email(request, user)
        except Exception as e:
            return JsonResponse({'success': False, 'errors': {'email': '发送邮件时出现错误，请稍后再试。'}})

    return JsonResponse(
        {'success': True, 'message': '如果该邮箱地址存在，重置密码的邮件已发送。请检查您的收件箱（包括垃圾邮件文件夹）。'})


def send_reset_password_email(request, user):
    models.PasswordResetToken.objects.filter(user=user).delete()

    reset_token = models.PasswordResetToken.objects.create(user=user)
    current_site = request.get_host()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    subject = '重置您的密码'
    message = render_to_string('blog/components/reset_password_email.html', {
        'user': user,
        'domain': current_site,
        'uid': uidb64,
        'token': reset_token.token,
    })
    email = EmailMessage(
        subject,
        message,
        None,
        [user.email]
    )
    email.content_subtype = 'html'
    email.send()


def confirm_reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.User.objects.get(pk=uid)
        reset_token = models.PasswordResetToken.objects.get(user=user, token=token)
        if reset_token.is_valid():
            if request.method == 'POST':
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    reset_token.delete()
                    return JsonResponse({'success': True, 'message': '密码已成功重置,请使用新密码登录。'})
                else:
                    return JsonResponse({'success': False, 'errors': '两次输入的密码不一致。'})
            return render(request, 'blog/auth/confirm_reset_password.html')
        else:
            return JsonResponse({'success': False, 'errors': '密码重置链接已过期。'})
    except (TypeError, ValueError, OverflowError, models.User.DoesNotExist, models.PasswordResetToken.DoesNotExist):
        return JsonResponse({'success': False, 'errors': '链接无效。'})
