from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('必须提供用户名')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),
        ('admin', '普通管理员'),
        ('teacher', '教师'),
    )
    
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher', verbose_name='角色')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否为员工')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
    
    def __str__(self):
        return self.username
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_admin(self):
        return self.role in ['super_admin', 'admin']

# 教师信息扩展模型
class TeacherInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_info', verbose_name='关联用户')
    name = models.CharField(max_length=100, verbose_name='姓名')
    education = models.CharField(max_length=100, verbose_name='学历')
    major = models.CharField(max_length=100, verbose_name='专业')
    teaching_scope = models.TextField(verbose_name='辅导范围')
    bank_account = models.CharField(max_length=100, verbose_name='银行账户')
    phone = models.CharField(max_length=20, verbose_name='联系方式')
    is_approved = models.BooleanField(default=False, verbose_name='是否已审核')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '教师信息'
        verbose_name_plural = '教师信息管理'
    
    def __str__(self):
        return f'{self.name}（{self.user.username}）'
    
    def get_bank_account_masked(self):
        """获取脱敏后的银行账户"""
        if len(self.bank_account) > 8:
            return f'{self.bank_account[:4]}****{self.bank_account[-4:]}'
        return self.bank_account

# 管理员信息扩展模型
class AdminInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_info', verbose_name='关联用户')
    name = models.CharField(max_length=100, verbose_name='姓名')
    phone = models.CharField(max_length=20, verbose_name='联系方式')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '管理员信息'
        verbose_name_plural = '管理员信息管理'
    
    def __str__(self):
        return f'{self.name}（{self.user.username}）'
