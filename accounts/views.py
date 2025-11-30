from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Sum, Count
from .forms import CustomAuthenticationForm, TeacherRegistrationForm, TeacherInfoForm, AdminInfoForm, AdminRegistrationForm
from .models import User, TeacherInfo, AdminInfo
from orders.models import OperationLog
import datetime
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

# 权限检查装饰器
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('无权访问')
        return wrapper
    return decorator

# 登录视图
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # 记录登录日志
            OperationLog.objects.create(
                user=user,
                action='login',
                object_type='User',
                object_id=user.id,
                object_name=user.username,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'用户{user.username}登录系统'
            )
            
            messages.success(request, '登录成功')
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# 登出视图
@login_required
def logout_view(request):
    # 记录登出日志
    OperationLog.objects.create(
        user=request.user,
        action='logout',
        object_type='User',
        object_id=request.user.id,
        object_name=request.user.username,
        ip_address=request.META.get('REMOTE_ADDR'),
        description=f'用户{request.user.username}登出系统'
    )
    
    logout(request)
    messages.success(request, '登出成功')
    return redirect('accounts:login')

# 教师注册视图
def teacher_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            # 创建用户
            user = form.save(commit=False)
            user.role = 'teacher'
            user.save()
            
            # 创建教师信息
            TeacherInfo.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                education=form.cleaned_data['education'],
                major=form.cleaned_data['major'],
                teaching_scope=form.cleaned_data['teaching_scope'],
                bank_account=form.cleaned_data['bank_account'],
                phone=form.cleaned_data['phone'],
                is_approved=False
            )
            
            messages.success(request, '注册成功，请等待管理员审核')
            return redirect('accounts:login')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# 管理员注册视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_register(request):
    """超级管理员创建普通管理员账号"""
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # 创建用户
            user = form.save(commit=False)
            user.role = 'admin'
            user.is_staff = True
            user.save()
            
            # 创建管理员信息
            AdminInfo.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone']
            )
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='create',
                object_type='Admin',
                object_id=user.id,
                object_name=user.username,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'超级管理员{request.user.username}创建了普通管理员{user.username}'
            )
            
            messages.success(request, '普通管理员账号创建成功！')
            return redirect('accounts:admin_list')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'admin/admin_register.html', {'form': form})

# 管理员列表视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_list(request):
    """超级管理员查看管理员列表"""
    from django.db.models import Q
    
    # 获取筛选参数
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    
    # 构建查询 - 只显示普通管理员，不显示超级管理员
    admins = User.objects.filter(role='admin')
    
    if search:
        admins = admins.filter(
            Q(username__icontains=search) |
            Q(admin_info__name__icontains=search) |
            Q(admin_info__phone__icontains=search)
        )
    
    if is_active == 'true':
        admins = admins.filter(is_active=True)
    elif is_active == 'false':
        admins = admins.filter(is_active=False)
    
    # 排序
    admins = admins.order_by('-id')
    
    context = {
        'admins': admins,
        'search': search,
        'is_active': is_active
    }
    
    return render(request, 'admin/admin_list.html', context)

# 管理员查看管理员详情视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_detail(request, pk):
    """超级管理员查看管理员详情"""
    # 首先检查用户是否存在
    admin = get_object_or_404(User, pk=pk)
    
    # 检查是否为普通管理员
    if admin.role != 'admin':
        messages.error(request, '只能查看普通管理员账号！')
        return redirect('accounts:admin_list')
    
    context = {
        'admin': admin
    }
    
    return render(request, 'admin/admin_detail.html', context)

# 管理员编辑管理员信息视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_edit(request, pk):
    """超级管理员编辑管理员信息"""
    # 首先检查用户是否存在
    admin = get_object_or_404(User, pk=pk)
    
    # 检查是否为普通管理员
    if admin.role != 'admin':
        messages.error(request, '只能编辑普通管理员账号！')
        return redirect('accounts:admin_list')
    
    try:
        admin_info = admin.admin_info
    except AdminInfo.DoesNotExist:
        admin_info = AdminInfo(user=admin)
    
    if request.method == 'POST':
        form = AdminInfoForm(request.POST, instance=admin_info)
        if form.is_valid():
            # 更新管理员信息
            admin_info = form.save()
            
            # 更新用户状态
            admin.is_active = 'is_active' in request.POST
            admin.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='update',
                object_type='Admin',
                object_id=admin.id,
                object_name=admin.username,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'超级管理员{request.user.username}编辑了管理员{admin.username}的信息'
            )
            
            messages.success(request, '管理员信息已更新！')
            return redirect('accounts:admin_detail', pk=admin.id)
    else:
        form = AdminInfoForm(instance=admin_info)
    
    context = {
        'admin': admin,
        'form': form
    }
    
    return render(request, 'admin/admin_edit.html', context)

# 管理员禁用/启用管理员账号视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_toggle(request, pk):
    """超级管理员禁用/启用管理员账号"""
    # 首先检查用户是否存在
    admin = get_object_or_404(User, pk=pk)
    
    # 检查是否为普通管理员
    if admin.role != 'admin':
        messages.error(request, '只能管理普通管理员账号！')
        return redirect('accounts:admin_list')
    
    # 切换管理员账号状态
    admin.is_active = not admin.is_active
    admin.save()
    
    # 记录操作日志
    action = 'enable' if admin.is_active else 'disable'
    OperationLog.objects.create(
        user=request.user,
        action=action,
        object_type='Admin',
        object_id=admin.id,
        object_name=admin.username,
        ip_address=request.META.get('REMOTE_ADDR'),
        description=f'超级管理员{request.user.username} {'启用' if admin.is_active else '禁用'}了管理员{admin.username}的账号'
    )
    
    messages.success(request, f'管理员账号已{'启用' if admin.is_active else '禁用'}！')
    return redirect('accounts:admin_list')

# 管理员删除管理员账号视图（仅超级管理员可访问）
@login_required
@role_required(['super_admin'])
def admin_delete(request, pk):
    """超级管理员删除管理员账号"""
    # 首先检查用户是否存在
    admin = get_object_or_404(User, pk=pk)
    
    # 检查是否为普通管理员
    if admin.role != 'admin':
        messages.error(request, '只能删除普通管理员账号！')
        return redirect('accounts:admin_list')
    
    # 记录操作日志
    OperationLog.objects.create(
        user=request.user,
        action='delete',
        object_type='Admin',
        object_id=admin.id,
        object_name=admin.username,
        ip_address=request.META.get('REMOTE_ADDR'),
        description=f'超级管理员{request.user.username}删除了管理员{admin.username}的账号'
    )
    
    # 删除管理员账号（级联删除会自动删除关联的AdminInfo）
    admin.delete()
    
    messages.success(request, '管理员账号已删除！')
    return redirect('accounts:admin_list')

# 仪表盘视图
@login_required
def dashboard(request):
    if request.user.is_admin:
        # 管理员仪表盘
        from orders.models import Order, SalaryApplication
        # 使用annotate优化查询
        total_teachers = User.objects.filter(role='teacher').count()
        total_orders = Order.objects.count()
        pending_applications = SalaryApplication.objects.filter(status='pending').count()
        approved_amount = SalaryApplication.objects.filter(status='approved').aggregate(
            total=Sum('apply_amount')
        )['total'] or 0
        
        # 获取最新订单列表（最近5个）
        latest_orders = Order.objects.order_by('-created_at')[:5]
        # 获取待审核工资申请列表
        pending_applications_list = SalaryApplication.objects.filter(status='pending').order_by('-created_at')[:5]
        
        context = {
            'total_teachers': total_teachers,
            'total_orders': total_orders,
            'pending_applications': pending_applications,
            'approved_amount': approved_amount,
            'latest_orders': latest_orders,
            'pending_applications_list': pending_applications_list,
        }
        return render(request, 'admin/dashboard.html', context)
    else:
        # 教师仪表盘
        from orders.models import Order, SalaryApplication
        # 获取教师最近的5个订单
        my_orders = Order.objects.filter(teacher=request.user).order_by('-created_at')[:5]
        # 获取教师最近的5个工资申请
        my_applications = SalaryApplication.objects.filter(teacher=request.user).order_by('-created_at')[:5]
        
        context = {
            'my_orders': my_orders,
            'my_applications': my_applications,
        }
        return render(request, 'teacher/dashboard.html', context)

# 个人信息编辑视图
@login_required
def profile_edit(request):
    if request.user.role == 'teacher':
        # 教师信息编辑
        try:
            teacher_info = request.user.teacher_info
        except TeacherInfo.DoesNotExist:
            teacher_info = TeacherInfo(user=request.user)
        
        if request.method == 'POST':
            form = TeacherInfoForm(request.POST, instance=teacher_info)
            if form.is_valid():
                teacher_info = form.save(commit=False)
                teacher_info.is_approved = False  # 修改后需要重新审核
                teacher_info.save()
                messages.success(request, '信息已更新，请等待管理员审核')
                return redirect('accounts:profile_edit')
        else:
            form = TeacherInfoForm(instance=teacher_info)
    
    elif request.user.is_admin:
        # 管理员信息编辑
        try:
            admin_info = request.user.admin_info
        except AdminInfo.DoesNotExist:
            admin_info = AdminInfo(user=request.user)
        
        if request.method == 'POST':
            form = AdminInfoForm(request.POST, instance=admin_info)
            if form.is_valid():
                form.save()
                messages.success(request, '信息已更新')
                return redirect('accounts:profile_edit')
        else:
            form = AdminInfoForm(instance=admin_info)
    
    else:
        return HttpResponseForbidden('无权访问')
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

# 管理员管理教师列表视图
@login_required
@role_required(['super_admin', 'admin'])
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def admin_teacher_list(request):
    """管理员查看教师列表"""
    from django.db.models import Q
    
    # 获取筛选参数
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    is_approved = request.GET.get('is_approved', '')
    
    # 构建查询
    teachers = User.objects.filter(role='teacher')
    
    if search:
        teachers = teachers.filter(
            Q(username__icontains=search) |
            Q(teacher_info__name__icontains=search) |
            Q(teacher_info__phone__icontains=search)
        )
    
    if is_active == 'true':
        teachers = teachers.filter(is_active=True)
    elif is_active == 'false':
        teachers = teachers.filter(is_active=False)
    
    if is_approved == 'true':
        teachers = teachers.filter(teacher_info__is_approved=True)
    elif is_approved == 'false':
        teachers = teachers.filter(teacher_info__is_approved=False)
    
    # 排序
    teachers = teachers.order_by('-id')
    
    context = {
        'teachers': teachers,
        'search': search,
        'is_active': is_active,
        'is_approved': is_approved
    }
    
    return render(request, 'admin/teacher_list.html', context)

# 管理员查看教师详情视图
@login_required
@role_required(['super_admin', 'admin'])
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def admin_teacher_detail(request, pk):
    """管理员查看教师详情"""
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    
    # 获取教师的订单和工资申请信息
    from orders.models import Order, SalaryApplication
    orders = Order.objects.filter(teacher=teacher).order_by('-created_at')[:10]
    applications = SalaryApplication.objects.filter(teacher=teacher).order_by('-created_at')[:10]
    
    context = {
        'teacher': teacher,
        'orders': orders,
        'applications': applications
    }
    
    return render(request, 'admin/teacher_detail.html', context)

# 管理员编辑教师信息视图
@login_required
@role_required(['super_admin'])
def admin_teacher_edit(request, pk):
    """管理员编辑教师信息（仅超级管理员可访问）"""
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    
    try:
        teacher_info = teacher.teacher_info
    except TeacherInfo.DoesNotExist:
        teacher_info = TeacherInfo(user=teacher)
    
    if request.method == 'POST':
        form = TeacherInfoForm(request.POST, request.FILES, instance=teacher_info)
        if form.is_valid():
            # 更新教师信息
            teacher_info = form.save()
            
            # 更新用户状态
            teacher.is_active = 'is_active' in request.POST
            teacher.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='update',
                object_type='Teacher',
                object_id=teacher.id,
                object_name=teacher.username,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'超级管理员{request.user.username}编辑了教师{teacher.username}的信息'
            )
            
            messages.success(request, '教师信息已更新！')
            return redirect('accounts:admin_teacher_detail', pk=teacher.id)
    else:
        form = TeacherInfoForm(instance=teacher_info)
    
    context = {
        'teacher': teacher,
        'form': form
    }
    
    return render(request, 'admin/teacher_edit.html', context)

# 管理员审核教师视图
@login_required
@role_required(['super_admin', 'admin'])
def admin_teacher_approve(request, pk):
    """管理员审核教师"""
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    
    try:
        teacher_info = teacher.teacher_info
        teacher_info.is_approved = True
        teacher_info.save()
        
        # 记录操作日志
        OperationLog.objects.create(
            user=request.user,
            action='approve',
            object_type='Teacher',
            object_id=teacher.id,
            object_name=teacher.username,
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'管理员{request.user.username}审核通过了教师{teacher.username}'
        )
        
        messages.success(request, '教师审核通过！')
    except TeacherInfo.DoesNotExist:
        messages.error(request, '教师信息不存在！')
    
    return redirect('accounts:admin_teacher_list')

# 管理员禁用/启用教师视图
@login_required
@role_required(['super_admin', 'admin'])
def admin_teacher_toggle(request, pk):
    """管理员禁用/启用教师账号（超级管理员和普通管理员均可访问）"""
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    
    # 切换教师账号状态
    teacher.is_active = not teacher.is_active
    teacher.save()
    
    # 记录操作日志
    action = 'enable' if teacher.is_active else 'disable'
    OperationLog.objects.create(
            user=request.user,
            action=action,
            object_type='Teacher',
            object_id=teacher.id,
            object_name=teacher.username,
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'管理员{request.user.username} {'启用' if teacher.is_active else '禁用'}了教师{teacher.username}的账号'
        )
    
    messages.success(request, f'教师账号已{'启用' if teacher.is_active else '禁用'}！')
    return redirect('accounts:admin_teacher_list')

# 管理员删除教师视图
@login_required
@role_required(['super_admin'])
def admin_teacher_delete(request, pk):
    """管理员删除教师账号（仅超级管理员可访问）"""
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    
    # 记录操作日志
    OperationLog.objects.create(
        user=request.user,
        action='delete',
        object_type='Teacher',
        object_id=teacher.id,
        object_name=teacher.username,
        ip_address=request.META.get('REMOTE_ADDR'),
        description=f'超级管理员{request.user.username}删除了教师{teacher.username}的账号'
    )
    
    # 删除教师账号（级联删除会自动删除关联的TeacherInfo）
    teacher.delete()
    
    messages.success(request, '教师账号已删除！')
    return redirect('accounts:admin_teacher_list')
