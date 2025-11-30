from django import forms
from .models import Order, SalaryApplication
from accounts.models import User

# 订单表单
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'teacher', 'student_count', 'service_type', 'unit_price', 'total_hours', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入订单名称'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'student_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.5'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '订单名称',
            'teacher': '分配教师',
            'student_count': '服务学生数',
            'service_type': '服务类型',
            'unit_price': '单价（元/小时）',
            'total_hours': '总时长（小时）',
            'status': '订单状态',
        }
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        # 只显示教师角色的用户
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')
    
    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        return cleaned_data

# 工资申请表单
class SalaryApplicationForm(forms.ModelForm):
    class Meta:
        model = SalaryApplication
        fields = ['order', 'apply_amount', 'proof_file', 'remarks']
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'apply_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'proof_file': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入备注（可选）'}),
        }
        labels = {
            'order': '选择订单',
            'apply_amount': '申请金额（元）',
            'proof_file': '证明材料',
            'remarks': '备注',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SalaryApplicationForm, self).__init__(*args, **kwargs)
        
        # 只显示当前教师的已完成订单，并且该订单没有待审核或已通过的工资申请
        if self.user:
            # 获取当前教师的已完成订单
            completed_orders = Order.objects.filter(teacher=self.user, status='completed')
            
            # 获取已有有效工资申请的订单ID列表
            applied_order_ids = SalaryApplication.objects.filter(
                order__in=completed_orders,
                status__in=['pending', 'approved']
            ).values_list('order_id', flat=True)
            
            # 排除已有有效工资申请的订单
            self.fields['order'].queryset = completed_orders.exclude(id__in=applied_order_ids)
    
    def clean_apply_amount(self):
        apply_amount = self.cleaned_data.get('apply_amount')
        order = self.cleaned_data.get('order')
        
        if order and apply_amount > order.total_amount:
            raise forms.ValidationError(f'申请金额不能超过订单总金额（{order.total_amount}元）')
        
        return apply_amount
    
    def clean_proof_file(self):
        proof_file = self.cleaned_data.get('proof_file')
        
        if proof_file:
            # 检查文件大小（3MB限制）
            if proof_file.size > 3 * 1024 * 1024:
                raise forms.ValidationError('证明材料大小不能超过3MB')
            
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if proof_file.content_type not in allowed_types:
                raise forms.ValidationError('只支持JPG、PNG图片和PDF文件')
        
        return proof_file