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

from blog import views
from reflective_jornal import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('get_verification_code/', views.get_verification_code),
    path('index/', views.index),
    re_path('^$', views.index),
    path('register/', views.register),
    path('logout/', views.logout),
    path('test', views.test),

    # 用户后台管理
    re_path(r'dashboard/$', views.dashboard),
    re_path(r'dashboard/edit/$', views.edit),

    re_path(r'^(?P<username>\w+)/$', views.homepage),

    # article detail
    re_path(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.blog_post),

    # media url
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

]