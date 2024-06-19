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
    # Admin and login/logout paths
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Index and registration
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),

    # verification code
    path('get_verification_code/', views.get_verification_code, name='get_verification_code'),

    # MDEditor
    path('mdeditor/', include('mdeditor.urls')),

    # Test path
    path('test/', views.test, name='test'),

    # User dashboard management
    path('dashboard/', views.dashboard, name='dashboard'),

    # User article management
    path('article/delete/<int:nid>/', views.delete_article, name='delete_article'),
    path('article/edit/', views.edit_article, name='create_article'),
    path('article/edit/<int:nid>/', views.edit_article, name='edit_article'),
    path('article/publish/<int:nid>/', views.publish_article, name='publish_article'),

    # User homepage and articles
    re_path(r'^(?P<username>\w+)/$', views.homepage, name='homepage'),
    re_path(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.blog_post, name='blog_post'),

    # Media URL
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
