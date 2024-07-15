"""reflective_jornal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

from blog.views import auth, generic, user, article
from reflective_jornal import settings

urlpatterns = [
    # Admin and login/logout paths
    path('admin/', admin.site.urls),
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('register/', auth.register, name='register'),
    path('reset_password/', auth.reset_password, name='reset_password'),
    path('reset_password/<uidb64>/<token>', auth.confirm_reset_password, name='confirm_reset_password'),

    # Index
    path('', generic.index, name='index'),
    path('index/', generic.index, name='index'),

    # verification code
    path('get_captcha/', generic.get_captcha, name='get_captcha'),

    #
    # article
    path('article/delete/<int:nid>/', article.delete_article, name='delete_article'),
    path('article/edit/', article.edit_article, name='create_article'),
    path('article/edit/<int:nid>/', article.edit_article, name='edit_article'),
    path('article/publish/<int:nid>/', article.publish_article, name='publish_article'),
    #
    # User
    path('user/<str:username>/', user.homepage, name='personal_homepage'),
    path('user/<str:username>/dashboard/', user.dashboard, name='dashboard'),
    # re_path(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.article_detail, name='article_detail')
    path('user/<str:username>/articles/<int:article_id>/', article.article_detail, name='article_detail'),

    # MDEditor
    path('mdeditor/', include('mdeditor.urls')),

    # Test path
    path('test/', generic.test, name='test'),

]

# Media URL ONLY IN DEV
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    ]
