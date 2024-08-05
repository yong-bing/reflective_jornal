import json

from django import forms

from blog.models import User, Article, Category, Tag


class UserRegisterForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}),
        error_messages={'required': '用户名不能为空', 'min_length': '用户名长度不能小于3个字符',
                        'max_length': '用户名长度不能大于20个字符'}
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '电子邮箱'}),
        error_messages={'invalid': '邮箱格式错误', 'required': '邮箱不能为空'})

    password = forms.CharField(
        max_length=20,
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}),
        error_messages={'required': '密码不能为空', 'min_length': '密码长度不能小于6个字符',
                        'max_length': '密码长度不能大于20个字符'}
    )
    confirm_password = forms.CharField(
        max_length=20,
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认密码'}),
        error_messages={'required': '确认密码不能为空', 'min_length': '确认密码长度不能小于6个字符',
                        'max_length': '确认密码长度不大于20个字符'}
    )

    # 用户名不唯一错误提示, 重写clean_username方法
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            raise forms.ValidationError('用户名已存在!')
        return username

    # 密码不一致错误提示, 重写clean方法, 全局验证
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('两次密码不一致!')
        return self.cleaned_data


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}),
        }


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'status', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入文章标题'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入文章内容'}),
            'status': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        super(ArticleCreateForm, self).__init__(*args, **kwargs)
        self.fields['author'].initial = self.author

    def save(self, commit=True):
        instance = super(ArticleCreateForm, self).save(commit=False)
        instance.author = self.author
        instance.status = 0
        if commit:
            instance.save()
        return instance


class ArticlePublishForm(forms.ModelForm):
    categories = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入文章分类，多个分类用英文逗号分隔...'
    }), label='文章分类')
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入文章标签，多个标签用英文逗号分隔...'
    }), label='文章标签')

    class Meta:
        model = Article
        fields = ['desc', 'cover', 'status', 'categories', 'tags']
        widgets = {
            'desc': forms.Textarea(
                attrs={
                    'class': 'form-control', 'placeholder': '请输入文章摘要...', 'rows': 3, 'style': 'resize:vertical'
                }),
            'cover': forms.FileInput(attrs={'class': 'd-none', 'id': 'coverUpload'}),
            'status': forms.HiddenInput(),
        }
        labels = {
            'desc': '文章摘要',
            'cover': '文章封面',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['categories'] = ', '.join(c.content for c in self.instance.categories.all())
            self.initial['tags'] = ', '.join(t.content for t in self.instance.tags.all())
        else:
            self.initial['categories'] = ''
            self.initial['tags'] = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = 1  # 设置为已发布状态
        if commit:
            instance.save()

            # 处理分类
            instance.categories.clear()
            categories = json.loads(self.cleaned_data['categories'])
            for item in categories:
                cat, created = Category.objects.get_or_create(content=item['value'])
                instance.categories.add(cat)

            # 处理标签
            instance.tags.clear()
            tags = json.loads(self.cleaned_data['tags'])
            for item in tags:
                tag, created = Tag.objects.get_or_create(content=item['value'])
                instance.tags.add(tag)

        return instance
