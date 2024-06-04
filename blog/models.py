from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class UserInfo(AbstractUser):
    """user info"""
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.jpg')
    create_time = models.DateTimeField(auto_now_add=True)

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """blog"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='blog title')
    site = models.CharField(max_length=32, unique=True, verbose_name='blog site')
    theme = models.CharField(max_length=32, verbose_name='blog theme')

    def __str__(self):
        return self.title


class Category(models.Model):
    """category"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='category title')
    blog = models.ForeignKey(to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """tag"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='tag title')
    blog = models.ForeignKey(to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    """article"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, verbose_name='article title')
    desc = models.CharField(max_length=255, verbose_name='article desc')
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    tags = models.ManyToManyField(
        to='Tag',
        through='Article2Tag',
        through_fields=('article', 'tag')
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag', to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag')
        ]

    def __str__(self):
        return self.article.title + '---' + self.tag.title


class Comment(models.Model):
    """comment"""
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey(to='self', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class ArticleUpDown(models.Model):
    """up or down"""
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('user', 'article')
        ]

    def __str__(self):
        return self.user.username + '---' + self.article.title
