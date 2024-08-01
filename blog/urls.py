from django.urls import path, include

from blog.views import auth, generic, article, user

urlpatterns = [
    # Admin and login/logout paths
    # path('admin/', admin.site.urls),
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('register/', auth.register, name='register'),
    path('reset-password/', auth.reset_password, name='reset_password'),
    path('reset-password/<uidb64>/<token>', auth.confirm_reset_password, name='confirm_reset_password'),

    # Index
    path('', generic.index, name='index'),
    path('index/', generic.index, name='index'),

    # verification code
    path('get-captcha/', generic.get_captcha, name='get_captcha'),

    # article
    path('article/delete/<str:article_id>/', article.delete_article, name='delete_article'),
    path('article/edit/', article.edit_article, name='create_article'),
    path('article/edit/<str:article_id>/', article.edit_article, name='edit_article'),
    path('article/publish/<str:article_id>/', article.publish_article, name='publish_article'),
    path('article/category/', article.category, name='category'),
    path('article/gabc/', article.get_articles_by_category, name='get_articles_bc'),

    # User
    path('user/<str:username>/', user.homepage, name='personal_homepage'),
    path('dashboard/', user.dashboard, name='dashboard'),
    path('<str:username>/articles/<str:article_id>/', article.article_detail, name='article_detail'),

    # MDEditor
    path('mdeditor/', include('mdeditor.urls')),

    # Test path
    path('test/', generic.test, name='test'),
]
