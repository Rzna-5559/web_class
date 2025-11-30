from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from .models import User, TeacherInfo, AdminInfo

class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('用户名或密码错误')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('账号已被禁用')
        return self.cleaned_data

class TeacherRegistrationForm(UserCreationForm):
    """教师注册表单"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    name = forms.CharField(
        label='姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'})
    )
    education = forms.CharField(
        label='学历',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入学历'})
    )
    major = forms.CharField(
        label='专业',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入专业'})
    )
    teaching_scope = forms.CharField(
        label='辅导范围',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入辅导范围', 'rows': 3})
    )
    bank_account = forms.CharField(
        label='银行账户',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入银行账户'})
    )
    phone = forms.CharField(
        label='联系方式',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class TeacherInfoForm(forms.ModelForm):
    """教师信息编辑表单"""
    class Meta:
        model = TeacherInfo
        fields = ['name', 'education', 'major', 'teaching_scope', 'bank_account', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'teaching_scope': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AdminInfoForm(forms.ModelForm):
    """管理员信息编辑表单"""
    class Meta:
        model = AdminInfo
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AdminRegistrationForm(UserCreationForm):
    """管理员注册表单（仅超级管理员可使用）"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    name = forms.CharField(
        label='姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'})
    )
    phone = forms.CharField(
        label='联系方式',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
