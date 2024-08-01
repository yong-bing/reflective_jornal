from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from blog import models

# Register your models here.


admin.site.register(models.Article)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Comment)
admin.site.register(models.Homepage)


# 使用admin录入数据时密码加密
@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'avatar', 'homepage', 'desc', 'signature']
    fieldsets = (
        (None, {'fields': ('username',
                           'password',
                           'email',
                           'avatar',
                           'homepage',
                           'desc',
                           'signature')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',
                       'password1',
                       'password2',
                       'email',
                       'avatar',
                       'homepage',
                       'desc',
                       'signature'
                       )}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()
