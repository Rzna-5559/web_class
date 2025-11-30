from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
import datetime
from .models import Order, SalaryApplication, OperationLog
from .forms import OrderForm, SalaryApplicationForm
from accounts.models import User, TeacherInfo
from accounts.views import role_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

# 管理员订单列表视图
@login_required
@role_required(['super_admin', 'admin'])
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def admin_order_list(request):
    # 获取筛选参数
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    # 构建查询
    orders = Order.objects.all()
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(name__icontains=search) |
            Q(teacher__username__icontains=search)
        )
    
    if status:
        orders = orders.filter(status=status)
    
    # 分页（暂时不实现）
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'search': search,
        'status': status,
        'status_choices': Order.STATUS_CHOICES
    }
    
    return render(request, 'orders/admin_order_list.html', context)

# 管理员创建订单视图
@login_required
@role_required(['super_admin', 'admin'])
def admin_order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user  # 设置当前登录用户为创建者
            order.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='create',
                object_type='Order',
                object_id=order.id,
                object_name=order.order_number,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'管理员{request.user.username}创建了订单{order.order_number}'
            )
            
            messages.success(request, '订单创建成功')
            return redirect('orders:admin_order_list')
    else:
        form = OrderForm()
    
    return render(request, 'orders/admin_order_create.html', {'form': form})

# 管理员编辑订单视图
@login_required
@role_required(['super_admin', 'admin'])
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            order = form.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='edit',
                object_type='Order',
                object_id=order.id,
                object_name=order.order_number,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'管理员{request.user.username}编辑了订单{order.order_number}'
            )
            
            messages.success(request, '订单编辑成功')
            return redirect('orders:admin_order_list')
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'orders/admin_order_edit.html', {'form': form, 'order': order})

# 管理员订单详情视图
@login_required
@role_required(['super_admin', 'admin'])
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/admin_order_detail.html', {'order': order})

# 教师订单列表视图
@login_required
@role_required(['teacher'])
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def teacher_order_list(request):
    # 获取筛选参数
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    # 获取当前教师的订单
    orders = Order.objects.filter(teacher=request.user)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(name__icontains=search)
        )
    
    if status:
        orders = orders.filter(status=status)
    
    # 分页（暂时不实现）
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'search': search,
        'status': status,
        'status_choices': Order.STATUS_CHOICES
    }
    
    return render(request, 'orders/teacher_order_list.html', context)

# 教师订单详情视图
@login_required
@role_required(['teacher'])
def teacher_order_detail(request, order_id):
    # 只能查看自己的订单
    order = get_object_or_404(Order, id=order_id, teacher=request.user)
    
    # 检查订单是否有工资申请记录
    application = SalaryApplication.objects.filter(order=order).first()
    
    # 处理订单状态切换
    if request.method == 'POST' and 'update_status' in request.POST:
        new_status = request.POST.get('new_status')
        old_status = order.status
        
        # 验证状态转换是否有效
        valid_transitions = {
            'pending': ['ongoing'],       # 待开课 -> 进行中
            'ongoing': ['completed'],     # 进行中 -> 已完成
            'completed': []               # 已完成不能再转换
        }
        
        if new_status in valid_transitions.get(old_status, []):
            order.status = new_status
            order.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='update',
                object_type='Order',
                object_id=order.id,
                object_name=order.order_number,
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'教师{request.user.username}将订单{order.order_number}状态从{dict(Order.STATUS_CHOICES).get(old_status)}更新为{dict(Order.STATUS_CHOICES).get(new_status)}'
            )
            
            messages.success(request, f'订单状态已成功更新为{dict(Order.STATUS_CHOICES).get(new_status)}')
        else:
            messages.error(request, '无效的状态转换')
        
        return redirect('orders:teacher_order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'application': application
    }
    
    return render(request, 'orders/teacher_order_detail.html', context)

# 工资申请列表视图
@login_required
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def salary_application_list(request):
    if request.user.is_admin:
        # 管理员查看所有申请
        applications = SalaryApplication.objects.all()
    else:
        # 教师只能查看自己的申请
        applications = SalaryApplication.objects.filter(teacher=request.user)
    
    # 获取筛选参数
    status = request.GET.get('status', '')
    
    if status:
        applications = applications.filter(status=status)
    
    # 分页（暂时不实现）
    applications = applications.order_by('-created_at')
    
    context = {
        'applications': applications,
        'status': status,
        'status_choices': SalaryApplication.STATUS_CHOICES
    }
    
    return render(request, 'orders/salary_application_list.html', context)

# 创建工资申请视图
@login_required
@role_required(['teacher'])
def salary_application_create(request):
    # 获取URL中的订单ID参数（如果有）
    order_id = request.GET.get('order_id')
    
    if request.method == 'POST':
        form = SalaryApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.teacher = request.user  # 设置当前登录教师
            application.status = 'pending'  # 设置初始状态为待审核
            application.apply_amount = form.cleaned_data['apply_amount']
            application.save()
            
            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,
                action='create',
                object_type='SalaryApplication',
                object_id=application.id,
                object_name=f'申请{application.id}',
                ip_address=request.META.get('REMOTE_ADDR'),
                description=f'教师{request.user.username}提交了工资申请{application.id}，申请金额：{application.apply_amount}元'
            )
            
            messages.success(request, '工资申请提交成功')
            return redirect('orders:salary_application_list')
    else:
        # 创建表单，并根据URL参数预选订单
        form = SalaryApplicationForm(user=request.user, initial={'order': order_id} if order_id else {})
    
    # 获取当前教师的所有工资申请记录（按时间倒序排序，显示最近的10条）
    existing_applications = SalaryApplication.objects.filter(teacher=request.user).order_by('-created_at')[:10]
    
    return render(request, 'orders/salary_application_create.html', {
        'form': form,
        'existing_applications': existing_applications
    })

# 工资申请详情视图
@login_required
def salary_application_detail(request, application_id):
    application = get_object_or_404(SalaryApplication, id=application_id)
    
    # 权限检查：只能查看自己的申请或管理员可以查看所有
    if not (application.teacher == request.user or request.user.is_admin):
        return HttpResponseForbidden('无权访问')
    
    return render(request, 'orders/salary_application_detail.html', {'application': application})

# 审核通过工资申请视图
@login_required
@role_required(['super_admin', 'admin'])
def salary_application_approve(request, application_id):
    application = get_object_or_404(SalaryApplication, id=application_id)
    
    if request.method == 'POST':
        application.status = 'approved'
        application.approved_at = datetime.datetime.now()
        application.approved_by = request.user
        application.remarks = request.POST.get('remarks', '')
        application.save()
        
        # 记录操作日志
        OperationLog.objects.create(
            user=request.user,
            action='approve',
            object_type='SalaryApplication',
            object_id=application.id,
            object_name=f'申请{application.id}',
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'管理员{request.user.username}通过了教师{application.teacher.username}的工资申请{application.id}'
        )
        
        messages.success(request, '工资申请审核通过')
        return redirect('orders:salary_application_list')
    
    return render(request, 'orders/salary_application_approve.html', {'application': application})

# 拒绝工资申请视图
@login_required
@role_required(['super_admin', 'admin'])
def salary_application_reject(request, application_id):
    application = get_object_or_404(SalaryApplication, id=application_id)
    
    if request.method == 'POST':
        application.status = 'rejected'
        application.rejected_at = datetime.datetime.now()
        application.approved_by = request.user
        application.rejection_reason = request.POST.get('remarks', '')
        application.save()
        
        # 记录操作日志
        OperationLog.objects.create(
            user=request.user,
            action='reject',
            object_type='SalaryApplication',
            object_id=application.id,
            object_name=f'申请{application.id}',
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'管理员{request.user.username}拒绝了教师{application.teacher.username}的工资申请{application.id}'
        )
        
        messages.success(request, '工资申请已拒绝')
        return redirect('orders:salary_application_list')
    
    return render(request, 'orders/salary_application_reject.html', {'application': application})

# 撤回工资申请视图
@login_required
@role_required(['teacher'])
def salary_application_withdraw(request, application_id):
    application = get_object_or_404(SalaryApplication, id=application_id, teacher=request.user)
    
    # 只能撤回待审核的申请
    if application.status != 'pending':
        messages.error(request, '只能撤回待审核的申请')
        return redirect('orders:salary_application_detail', application_id=application_id)
    
    if request.method == 'POST':
        application.status = 'withdrawn'
        application.save()
        
        # 记录操作日志
        OperationLog.objects.create(
            user=request.user,
            action='withdraw',
            object_type='SalaryApplication',
            object_id=application.id,
            object_name=f'申请{application.id}',
            ip_address=request.META.get('REMOTE_ADDR'),
            description=f'教师{request.user.username}撤回了工资申请{application.id}'
        )
        
        messages.success(request, '工资申请已撤回')
        return redirect('orders:salary_application_list')
    
    return render(request, 'orders/salary_application_withdraw.html', {'application': application})

# 日志管理视图
@login_required
@role_required(['super_admin', 'admin'])
@cache_page(60 * 5)  # 缓存5分钟
@vary_on_cookie
@vary_on_headers('User-Agent')
def log_list(request):
    """管理员查看操作日志列表"""
    # 获取筛选参数
    search = request.GET.get('search', '')
    action = request.GET.get('action', '')
    user_id = request.GET.get('user', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # 构建查询
    logs = OperationLog.objects.all()
    
    if search:
        logs = logs.filter(
            Q(description__icontains=search) |
            Q(object_name__icontains=search) |
            Q(ip_address__icontains=search)
        )
    
    if action:
        logs = logs.filter(action=action)
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    if start_date:
        logs = logs.filter(created_at__gte=start_date)
    
    if end_date:
        logs = logs.filter(created_at__lte=end_date + ' 23:59:59')
    
    # 分页（暂时不实现）
    logs = logs.order_by('-created_at')
    
    # 获取所有用户（用于筛选）
    users = User.objects.all()
    
    context = {
        'logs': logs,
        'search': search,
        'action': action,
        'user_id': user_id,
        'start_date': start_date,
        'end_date': end_date,
        'users': users,
        'action_choices': OperationLog.ACTION_CHOICES
    }
    
    return render(request, 'admin/log_list.html', context)

# 数据备份恢复视图
@login_required
@role_required(['super_admin', 'admin'])
def data_backup(request):
    """数据备份和恢复功能"""
    import os
    import datetime
    import subprocess
    from django.conf import settings
    from django.http import HttpResponse, FileResponse
    from django.contrib import messages
    from .models import OperationLog
    
    # 备份文件保存目录
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 获取现有备份列表
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(backup_dir, filename)
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                backups.append({
                    'filename': filename,
                    'size': size,
                    'mtime': datetime.datetime.fromtimestamp(mtime)
                })
    backups.sort(key=lambda x: x['mtime'], reverse=True)
    
    if request.method == 'POST':
        if 'backup' in request.POST:
            # 创建备份
            try:
                backup_filename = f'backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
                backup_path = os.path.join(backup_dir, backup_filename)
                
                # 使用sqlite3命令导出数据库
                if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
                    db_path = settings.DATABASES['default']['NAME']
                    cmd = f'sqlite3 {db_path} ".backup {backup_path}"'
                    subprocess.run(cmd, shell=True, check=True)
                
                # 记录操作日志
                OperationLog.objects.create(
                    user=request.user,
                    action='create',
                    object_type='Backup',
                    object_id='0',
                    object_name=backup_filename,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    description=f'管理员{request.user.username}创建了数据备份：{backup_filename}'
                )
                
                messages.success(request, '数据备份成功！')
                return redirect('orders:data_backup')
            except Exception as e:
                messages.error(request, f'数据备份失败：{str(e)}')
                return redirect('orders:data_backup')
        
        elif 'restore' in request.POST and 'backup_file' in request.FILES:
            # 恢复备份
            try:
                backup_file = request.FILES['backup_file']
                restore_path = os.path.join(backup_dir, f'restore_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.sql')
                
                # 保存上传的备份文件
                with open(restore_path, 'wb+') as destination:
                    for chunk in backup_file.chunks():
                        destination.write(chunk)
                
                # 使用sqlite3命令导入数据库
                if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
                    db_path = settings.DATABASES['default']['NAME']
                    cmd = f'sqlite3 {db_path} ".restore {restore_path}"'
                    subprocess.run(cmd, shell=True, check=True)
                
                # 记录操作日志
                OperationLog.objects.create(
                    user=request.user,
                    action='update',
                    object_type='Database',
                    object_id='0',
                    object_name='Database',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    description=f'管理员{request.user.username}从备份文件{backup_file.name}恢复了数据'
                )
                
                messages.success(request, '数据恢复成功！')
                return redirect('orders:data_backup')
            except Exception as e:
                messages.error(request, f'数据恢复失败：{str(e)}')
                return redirect('orders:data_backup')
        
        elif 'download' in request.POST and 'filename' in request.POST:
            # 下载备份文件
            filename = request.POST['filename']
            filepath = os.path.join(backup_dir, filename)
            
            if os.path.exists(filepath):
                return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
            else:
                messages.error(request, '备份文件不存在！')
                return redirect('orders:data_backup')
        
        elif 'delete' in request.POST and 'filename' in request.POST:
            # 删除备份文件
            filename = request.POST['filename']
            filepath = os.path.join(backup_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                messages.success(request, '备份文件删除成功！')
            else:
                messages.error(request, '备份文件不存在！')
            return redirect('orders:data_backup')
    
    context = {
        'backups': backups,
        'backup_dir': backup_dir
    }
    
    return render(request, 'admin/data_backup.html', context)
