from django import forms

from blog.models import User, Article


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
        self.user = kwargs.pop('user')
        super(ArticleCreateForm, self).__init__(*args, **kwargs)
        self.fields['user'].initial = self.user

    def save(self, commit=True):
        instance = super(ArticleCreateForm, self).save(commit=False)
        instance.user = self.user
        instance.status = 0
        if commit:
            instance.save()
        return instance


class ArticlePublishForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['desc', 'cover', 'status']
        widgets = {
            'desc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入文章摘要...'}),
            'cover': forms.FileInput(attrs={'class': 'd-none', 'id': 'coverUpload'}),
            'status': forms.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super(ArticlePublishForm, self).save(commit=False)
        instance.status = 1
        if commit:
            instance.save()
        return instance
