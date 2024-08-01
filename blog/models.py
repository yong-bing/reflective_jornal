import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from mdeditor.fields import MDTextField


# Create your models here.

class User(AbstractUser):
    """user info"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.jpg')
    create_time = models.DateTimeField(auto_now_add=True)
    desc = models.CharField(max_length=255, null=True)
    signature = models.CharField(max_length=255, null=True)

    homepage = models.OneToOneField(to='Homepage', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Homepage(models.Model):
    """blog"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64, verbose_name='homepage title')
    url = models.CharField(max_length=32, unique=True, verbose_name='homepage url')

    def __str__(self):
        return self.title


class Category(models.Model):
    """category"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=32, verbose_name='category content')

    def __str__(self):
        return self.content


class Tag(models.Model):
    """tag"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=32, verbose_name='tag content')

    def __str__(self):
        return self.content


class Article(models.Model):
    """article"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=128, verbose_name='article title')
    desc = models.CharField(max_length=255, verbose_name='article desc')
    cover = models.FileField(upload_to='covers/', default='covers/default.jpg')
    # content = models.TextField()
    content = MDTextField()
    created_time = models.DateTimeField(auto_now_add=True)
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    author = models.ForeignKey(to='User', to_field='nid', on_delete=models.CASCADE, related_name='articles')
    status = models.IntegerField(choices=((0, 'draft'), (1, 'published')), default=0)
    views = models.IntegerField(default=0)
    categories = models.ManyToManyField('Category')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


# class Article2Tag(models.Model):
#     nid = models.AutoField(primary_key=True)
#     article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
#     tag = models.ForeignKey(to='Tag',  on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.article.title + '---' + self.tag.content


# class Article2Category(models.Model):
#     nid = models.AutoField(primary_key=True)
#     article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
#     category = models.ForeignKey(to='Category', on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.article.title + '---' + self.category.content


class Comment(models.Model):
    """comment"""
    # nid = models.AutoField(primary_key=True)
    nid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(to='User', to_field='nid', on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey(
        to='self', to_field='nid', null=True, on_delete=models.CASCADE, related_name='child_comments')

    def __str__(self):
        return self.content


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at
