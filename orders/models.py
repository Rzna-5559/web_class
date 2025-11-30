from django.db import models
from django.utils import timezone
from accounts.models import User

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待开课'),
        ('ongoing', '进行中'),
        ('completed', '已完成'),
    )
    
    SERVICE_TYPE_CHOICES = (
        ('one_to_one', '一对一'),
        ('one_to_two', '一对二'),
        ('custom', '自定义'),
    )
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    name = models.CharField(max_length=200, verbose_name='订单名称')
    student_count = models.IntegerField(verbose_name='服务学生数')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, verbose_name='服务类型')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总时长')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='分配教师')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.order_number} - {self.name}'
    
    def save(self, *args, **kwargs):
        # 自动计算总金额
        if self.unit_price and self.total_hours:
            self.total_amount = self.unit_price * self.total_hours
        # 生成订单编号（如果没有）
        if not self.order_number:
            # 生成格式：ORD + 年月日 + 6位随机数
            prefix = timezone.now().strftime('ORD%Y%m%d')
            last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
            if last_order:
                sequence = int(last_order.order_number[-6:]) + 1
            else:
                sequence = 1
            self.order_number = f'{prefix}{sequence:06d}'
        super().save(*args, **kwargs)

class SalaryApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '通过'),
        ('rejected', '拒绝'),
        ('withdrawn', '已撤回'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='salary_applications', verbose_name='关联订单')
    application_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='申请编号')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_applications', verbose_name='申请教师')
    apply_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='申请金额')
    proof_file = models.FileField(upload_to='proofs/', verbose_name='证明材料')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_applications', verbose_name='审批人')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')
    rejection_reason = models.TextField(null=True, blank=True, verbose_name='拒绝原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    withdrawn_at = models.DateTimeField(null=True, blank=True, verbose_name='撤回时间')
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name='拒绝时间')
    
    class Meta:
        verbose_name = '工资申请'
        verbose_name_plural = '工资申请管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.application_number or "未生成编号"} - {self.order.order_number} - {self.teacher.username}'
    
    def save(self, *args, **kwargs):
        # 如果是首次保存，自动设置教师为订单的教师
        if not self.pk:
            self.teacher = self.order.teacher
        
        # 生成申请编号（如果没有）
        if not self.application_number:
            # 生成格式：APP + 年月日 + 6位随机数
            prefix = timezone.now().strftime('APP%Y%m%d')
            last_application = SalaryApplication.objects.filter(application_number__startswith=prefix).order_by('-application_number').first()
            if last_application:
                sequence = int(last_application.application_number[-6:]) + 1
            else:
                sequence = 1
            self.application_number = f'{prefix}{sequence:06d}'
        
        super().save(*args, **kwargs)

# 操作日志模型
class OperationLog(models.Model):
    ACTION_CHOICES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('approve', '审核通过'),
        ('reject', '审核拒绝'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs', verbose_name='操作用户')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    object_type = models.CharField(max_length=100, verbose_name='操作对象类型')
    object_id = models.CharField(max_length=100, verbose_name='操作对象ID')
    object_name = models.CharField(max_length=200, verbose_name='操作对象名称')
    ip_address = models.CharField(max_length=50, verbose_name='IP地址')
    description = models.TextField(verbose_name='操作描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user} - {self.get_action_display()} - {self.object_name}'
