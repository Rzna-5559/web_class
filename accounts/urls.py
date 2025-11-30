from django.urls import path
from .views import (
    login_view, logout_view, teacher_register, dashboard, profile_edit,
    admin_teacher_list, admin_teacher_detail, admin_teacher_edit,
    admin_teacher_approve, admin_teacher_toggle, admin_teacher_delete,
    admin_register, admin_list, admin_detail, admin_edit, admin_toggle, admin_delete
)

app_name = 'accounts'

urlpatterns = [
    # 基础功能
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', teacher_register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    
    # 管理员教师管理
    path('admin/teachers/', admin_teacher_list, name='admin_teacher_list'),
    path('admin/teachers/<int:pk>/', admin_teacher_detail, name='admin_teacher_detail'),
    path('admin/teachers/<int:pk>/edit/', admin_teacher_edit, name='admin_teacher_edit'),
    path('admin/teachers/<int:pk>/approve/', admin_teacher_approve, name='admin_teacher_approve'),
    path('admin/teachers/<int:pk>/toggle/', admin_teacher_toggle, name='admin_teacher_toggle'),
    path('admin/teachers/<int:pk>/delete/', admin_teacher_delete, name='admin_teacher_delete'),
    
    # 管理员管理（仅超级管理员可访问）
    path('admin/admins/', admin_list, name='admin_list'),
    path('admin/admins/register/', admin_register, name='admin_register'),
    path('admin/admins/<int:pk>/', admin_detail, name='admin_detail'),
    path('admin/admins/<int:pk>/edit/', admin_edit, name='admin_edit'),
    path('admin/admins/<int:pk>/toggle/', admin_toggle, name='admin_toggle'),
    path('admin/admins/<int:pk>/delete/', admin_delete, name='admin_delete'),
]