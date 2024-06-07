from django.contrib import admin

from blog import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Article)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article2Tag)
admin.site.register(models.Article2Category)
admin.site.register(models.Comment)
admin.site.register(models.Homepage)
