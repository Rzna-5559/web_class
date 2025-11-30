from django.urls import path
from .views import (
    admin_order_list, admin_order_create, admin_order_edit, admin_order_detail,
    teacher_order_list, teacher_order_detail,
    salary_application_list, salary_application_create, salary_application_detail,
    salary_application_approve, salary_application_reject, salary_application_withdraw,
    log_list, data_backup
)

app_name = 'orders'

urlpatterns = [
    # 管理员订单管理
    path('admin/orders/', admin_order_list, name='admin_order_list'),
    path('admin/orders/create/', admin_order_create, name='admin_order_create'),
    path('admin/orders/<int:order_id>/edit/', admin_order_edit, name='admin_order_edit'),
    path('admin/orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    
    # 教师订单管理
    path('teacher/orders/', teacher_order_list, name='teacher_order_list'),
    path('teacher/orders/<int:order_id>/', teacher_order_detail, name='teacher_order_detail'),
    
    # 工资申请管理
    path('applications/', salary_application_list, name='salary_application_list'),
    path('teacher/applications/', salary_application_list, name='teacher_salary_application_list'),
    path('teacher/applications/create/', salary_application_create, name='salary_application_create'),
    path('applications/<int:application_id>/', salary_application_detail, name='salary_application_detail'),
    path('applications/<int:application_id>/approve/', salary_application_approve, name='salary_application_approve'),
    path('applications/<int:application_id>/reject/', salary_application_reject, name='salary_application_reject'),
    path('applications/<int:application_id>/withdraw/', salary_application_withdraw, name='salary_application_withdraw'),
    
    # 日志管理相关路由
    path('log/', log_list, name='admin_log_list'),
    # 数据备份相关路由
    path('backup/', data_backup, name='data_backup'),
]