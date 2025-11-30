# 课程进度管理系统 - 阮老师个人学习项目

## 1. 项目概述

### 1.1 项目简介
Class_os（课程进度管理系统）是一个专为教育机构设计的综合管理系统，主要用于管理班级学生订单、教师信息和工资申请流程。系统采用Django框架开发，具有完善的角色权限控制和数据管理功能，帮助教育机构高效管理日常教学和行政事务。

### 1.2 项目定位
本项目定位为面向中小型教育机构的轻量化管理系统，主要解决教育机构在订单管理、教师管理和工资申请流程中的痛点问题。

### 1.3 项目特点
- **角色权限管理**：支持超级管理员、普通管理员和教师三种角色，权限分明
- **订单全流程管理**：从订单创建、状态跟踪到完成的完整管理
- **工资申请审批**：教师可提交工资申请，管理员审核批准
- **数据安全保障**：操作日志记录和数据备份恢复功能
- **响应式设计**：适配不同设备的访问需求

## 2. 技术栈

### 2.1 后端技术
- **框架**：Django 5.2.8
- **数据库**：SQLite（开发环境），PostgreSQL/MySQL（推荐生产环境）
- **认证系统**：基于Django的自定义用户认证
- **文件存储**：本地文件系统

### 2.2 前端技术
- **基础框架**：Bootstrap 5
- **图标库**：Font Awesome
- **模板引擎**：Django Templates
- **JavaScript**：原生JavaScript

### 2.3 开发环境
- **Python版本**：3.8+
- **操作系统**：Windows/macOS/Linux
- **编辑器推荐**：VS Code, PyCharm

## 3. 项目结构

### 3.1 整体结构
```
Class_os/
├── accounts/              # 账号管理应用
│   ├── migrations/        # 数据库迁移文件
│   ├── __init__.py        # 应用初始化文件
│   ├── admin.py           # Django后台管理配置
│   ├── apps.py            # 应用配置
│   ├── decorators.py      # 自定义装饰器（如权限控制）
│   ├── forms.py           # 表单定义
│   ├── models.py          # 数据模型定义
│   ├── tests.py           # 测试文件
│   ├── urls.py            # URL路由配置
│   └── views.py           # 视图函数定义
├── backups/               # 数据备份文件存储目录
├── class_os/              # Django项目配置目录
│   ├── __init__.py        # 项目初始化文件
│   ├── asgi.py            # ASGI服务器配置
│   ├── settings.py        # 项目主配置文件
│   ├── urls.py            # 项目主URL路由配置
│   └── wsgi.py            # WSGI服务器配置
├── db.sqlite3             # SQLite数据库文件
├── manage.py              # Django项目管理脚本
├── media/                 # 用户上传媒体文件目录
│   └── proofs/            # 工资申请证明文件
├── orders/                # 订单管理应用
│   ├── migrations/        # 数据库迁移文件
│   ├── __init__.py        # 应用初始化文件
│   ├── admin.py           # Django后台管理配置
│   ├── apps.py            # 应用配置
│   ├── forms.py           # 表单定义
│   ├── models.py          # 数据模型定义
│   ├── tests.py           # 测试文件
│   ├── urls.py            # URL路由配置
│   └── views.py           # 视图函数定义
├── static/                # 静态资源文件目录
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── img/               # 图片资源
├── templates/             # HTML模板文件目录
│   ├── accounts/          # 账号管理相关模板
│   ├── admin/             # 管理员页面模板
│   ├── base.html          # 基础模板
│   ├── orders/            # 订单和工资申请相关模板
│   └── teacher/           # 教师页面模板
├── README.md              # 项目说明文档
└── requirements.txt       # 项目依赖文件
```

### 3.2 核心模块说明

#### 3.2.1 账号管理模块 (accounts)
负责用户认证、角色管理和权限控制，包括登录、注册、个人资料管理等功能。

#### 3.2.2 订单管理模块 (orders)
负责订单的创建、编辑、状态跟踪和查询，以及工资申请的提交、审批等功能。

#### 3.2.3 系统配置模块 (class_os)
负责项目的整体配置，包括数据库、静态文件、中间件、安全设置等。

## 4. 数据模型设计

### 4.1 用户模型 (User)

**核心字段：**
- `username`：用户名（唯一标识）
- `role`：角色（super_admin, admin, teacher）
- `is_active`：账号是否激活
- `is_staff`：是否为员工
- `created_at`：创建时间
- `updated_at`：更新时间

**扩展属性：**
- `is_super_admin`：是否为超级管理员
- `is_admin`：是否为管理员（包括超级管理员）

**关联关系：**
- 与TeacherInfo或AdminInfo一对一关联

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),
        ('admin', '普通管理员'),
        ('teacher', '教师'),
    )
    
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher', verbose_name='角色')
    # 其他字段...
```

### 4.2 教师信息模型 (TeacherInfo)

**核心字段：**
- `user`：关联用户（一对一）
- `name`：姓名
- `education`：学历
- `major`：专业
- `teaching_scope`：辅导范围
- `bank_account`：银行账户
- `phone`：联系方式
- `is_approved`：是否已审核

**方法：**
- `get_bank_account_masked()`：获取脱敏后的银行账户

```python
class TeacherInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_info', verbose_name='关联用户')
    # 其他字段...
    
    def get_bank_account_masked(self):
        """获取脱敏后的银行账户"""
        if len(self.bank_account) > 8:
            return f'{self.bank_account[:4]}****{self.bank_account[-4:]}'
        return self.bank_account
```

### 4.3 管理员信息模型 (AdminInfo)

**核心字段：**
- `user`：关联用户（一对一）
- `name`：姓名
- `phone`：联系方式

```python
class AdminInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_info', verbose_name='关联用户')
    # 其他字段...
```

### 4.4 订单模型 (Order)

**核心字段：**
- `order_number`：订单编号
- `name`：订单名称
- `student_count`：服务学生数
- `service_type`：服务类型（一对一、一对二、自定义）
- `unit_price`：单价
- `total_hours`：总时长
- `total_amount`：总金额
- `status`：订单状态（待开课、进行中、已完成）
- `teacher`：分配教师
- `created_by`：创建人

**方法：**
- `save()`：自动计算总金额，生成订单编号

```python
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待开课'),
        ('ongoing', '进行中'),
        ('completed', '已完成'),
    )
    
    # 其他字段...
    
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
```

### 4.5 工资申请模型 (SalaryApplication)

**核心字段：**
- `order`：关联订单
- `application_number`：申请编号
- `teacher`：申请教师
- `apply_amount`：申请金额
- `proof_file`：证明材料
- `status`：审核状态（待审核、通过、拒绝、已撤回）
- `approved_by`：审批人
- `remarks`：备注
- `rejection_reason`：拒绝原因

**方法：**
- `save()`：自动设置教师为订单教师，生成申请编号

```python
class SalaryApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '通过'),
        ('rejected', '拒绝'),
        ('withdrawn', '已撤回'),
    )
    
    # 其他字段...
    
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
```

### 4.6 操作日志模型 (OperationLog)

**核心字段：**
- `user`：操作用户
- `action`：操作类型（登录、登出、创建、更新、删除、审核通过、审核拒绝）
- `object_type`：操作对象类型
- `object_id`：操作对象ID
- `object_name`：操作对象名称
- `ip_address`：IP地址
- `description`：操作描述
- `created_at`：操作时间

```python
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
    
    # 其他字段...
```

## 5. 系统架构与流程

### 5.1 系统架构

#### 5.1.1 分层架构
- **表现层**：Django Templates + Bootstrap + JavaScript
- **业务逻辑层**：Django Views + Forms
- **数据访问层**：Django ORM
- **数据存储层**：SQLite/PostgreSQL/MySQL

#### 5.1.2 核心流程图

```
用户认证流程
[用户] → 登录页面 → 提交凭证 → [认证系统] → 验证用户 → 授权访问 → [用户仪表盘]
```

```
订单管理流程
[管理员] → 创建订单 → 分配教师 → [订单状态: 待开课] → 
[教师] → 更新状态 → [订单状态: 进行中] → 
[教师] → 完成订单 → [订单状态: 已完成] → 
[教师] → 提交工资申请 → [管理员] → 审核 → [工资申请状态: 通过/拒绝]
```

### 5.2 关键业务流程

#### 5.2.1 订单管理流程
1. **创建订单**
   - 管理员登录系统
   - 进入订单管理页面
   - 填写订单信息（订单名称、学生数量、服务类型、单价、总时长等）
   - 选择分配的教师
   - 提交表单，系统自动生成订单编号和计算总金额
   - 订单状态初始化为"待开课"

2. **更新订单状态**
   - 教师登录系统
   - 进入教师订单列表页面
   - 选择要更新的订单
   - 在订单详情页面，根据教学进度更新状态
   - 系统记录状态变更日志

3. **编辑订单**
   - 管理员登录系统
   - 进入订单详情页面
   - 点击编辑按钮
   - 修改订单信息
   - 提交更新，系统记录操作日志

#### 5.2.2 工资申请流程
1. **提交工资申请**
   - 教师登录系统
   - 进入工资申请页面
   - 选择已完成的订单
   - 填写申请金额
   - 上传证明材料（如课时记录、学生签字等）
   - 提交申请，系统自动生成申请编号
   - 申请状态初始化为"待审核"

2. **审核工资申请**
   - 管理员登录系统
   - 进入工资申请列表页面
   - 查看待审核的申请
   - 点击申请详情，查看详细信息和证明材料
   - 根据审核结果进行操作：
     - 批准：更新状态为"通过"，记录审批人信息
     - 拒绝：更新状态为"拒绝"，填写拒绝原因，记录审批人信息

3. **撤回工资申请**
   - 教师登录系统
   - 进入工资申请列表页面
   - 找到待审核的申请
   - 点击"撤回"按钮
   - 确认撤回操作
   - 申请状态更新为"已撤回"

#### 5.2.3 教师管理流程
1. **教师注册**
   - 教师访问注册页面
   - 填写注册信息（用户名、密码、基本个人信息等）
   - 提交注册申请
   - 系统创建教师账户，状态为"待审核"

2. **审核教师**
   - 管理员登录系统
   - 进入教师管理页面
   - 查看待审核的教师列表
   - 点击教师详情，查看注册信息
   - 审核通过后，激活教师账户

3. **编辑教师信息**
   - 管理员登录系统
   - 进入教师管理页面
   - 选择要编辑的教师
   - 修改教师信息
   - 保存更新，系统记录操作日志

4. **禁用/启用教师账户**
   - 管理员登录系统
   - 进入教师列表页面
   - 找到目标教师
   - 点击"禁用"或"启用"按钮
   - 系统更新教师账户状态，记录操作日志

## 6. 功能模块详细说明

### 6.1 账号管理模块 (accounts)

#### 6.1.1 用户认证
- **登录功能**：用户通过用户名和密码登录系统
- **登出功能**：用户安全退出系统
- **密码重置**：支持密码找回功能（预留接口）

#### 6.1.2 个人资料管理
- **教师个人资料**：教师可查看和编辑自己的个人信息
- **管理员个人资料**：管理员可查看和编辑自己的个人信息

#### 6.1.3 教师管理（管理员功能）
- **教师列表**：查看所有教师信息，支持搜索和筛选
- **教师审核**：审核新注册的教师账户
- **编辑教师**：修改教师的个人信息和教学信息
- **禁用/启用**：控制教师账户的激活状态
- **删除教师**：永久删除教师账户（超级管理员权限）

#### 6.1.4 管理员管理（超级管理员功能）
- **管理员列表**：查看所有管理员信息
- **创建管理员**：创建新的普通管理员账户
- **编辑管理员**：修改管理员信息
- **禁用/启用**：控制管理员账户的激活状态
- **删除管理员**：永久删除管理员账户

### 6.2 订单管理模块 (orders)

#### 6.2.1 订单管理
- **订单列表**：查看所有订单，支持按状态、教师、时间等筛选
- **订单创建**：创建新的辅导订单
- **订单编辑**：修改订单信息
- **订单详情**：查看订单的详细信息
- **状态更新**：更新订单的状态（待开课→进行中→已完成）

#### 6.2.2 工资申请管理
- **申请列表**：查看所有工资申请，支持按状态、教师、时间等筛选
- **申请创建**：教师提交工资申请
- **申请详情**：查看工资申请的详细信息和证明材料
- **申请审批**：管理员审批工资申请（批准或拒绝）
- **申请撤回**：教师撤回待审核的工资申请

#### 6.2.3 日志管理
- **操作日志**：记录系统中所有关键操作
- **日志查询**：按时间、用户、操作类型等条件查询日志
- **日志详情**：查看操作的详细信息

#### 6.2.4 数据备份与恢复
- **备份管理**：查看和管理所有备份文件
- **手动备份**：手动触发数据备份
- **自动备份**：系统定时自动备份数据
- **数据恢复**：从备份文件恢复数据库

## 7. URL路由设计

### 7.1 项目主路由 (class_os/urls.py)
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('', dashboard, name='dashboard'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 7.2 账号管理路由 (accounts/urls.py)
```python
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 用户认证
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 个人资料
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # 管理员功能
    path('admin/teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('admin/teachers/<int:teacher_id>/', views.admin_teacher_detail, name='admin_teacher_detail'),
    path('admin/teachers/<int:teacher_id>/edit/', views.admin_teacher_edit, name='admin_teacher_edit'),
    path('admin/teachers/<int:teacher_id>/toggle/', views.admin_teacher_toggle, name='admin_teacher_toggle'),
    path('admin/teachers/<int:teacher_id>/delete/', views.admin_teacher_delete, name='admin_teacher_delete'),
    
    path('admin/admins/', views.admin_admin_list, name='admin_admin_list'),
    path('admin/admins/create/', views.admin_admin_create, name='admin_admin_create'),
    path('admin/admins/<int:admin_id>/edit/', views.admin_admin_edit, name='admin_admin_edit'),
    path('admin/admins/<int:admin_id>/toggle/', views.admin_admin_toggle, name='admin_admin_toggle'),
    path('admin/admins/<int:admin_id>/delete/', views.admin_admin_delete, name='admin_admin_delete'),
]
```

### 7.3 订单管理路由 (orders/urls.py)
```python
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # 订单管理
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/create/', views.admin_order_create, name='admin_order_create'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<int:order_id>/edit/', views.admin_order_edit, name='admin_order_edit'),
    
    # 教师订单管理
    path('teacher/orders/', views.teacher_order_list, name='teacher_order_list'),
    path('teacher/orders/<int:order_id>/', views.teacher_order_detail, name='teacher_order_detail'),
    path('teacher/orders/<int:order_id>/update-status/', views.teacher_order_update_status, name='teacher_order_update_status'),
    
    # 工资申请
    path('applications/', views.salary_application_list, name='salary_application_list'),
    path('teacher/applications/', views.teacher_salary_application_list, name='teacher_salary_application_list'),
    path('teacher/applications/create/', views.teacher_salary_application_create, name='teacher_salary_application_create'),
    path('applications/<int:application_id>/', views.salary_application_detail, name='salary_application_detail'),
    path('applications/<int:application_id>/approve/', views.salary_application_approve, name='salary_application_approve'),
    path('applications/<int:application_id>/reject/', views.salary_application_reject, name='salary_application_reject'),
    path('applications/<int:application_id>/withdraw/', views.salary_application_withdraw, name='salary_application_withdraw'),
    
    # 日志和备份
    path('admin/logs/', views.admin_log_list, name='admin_log_list'),
    path('admin/backup/', views.admin_backup_list, name='admin_backup_list'),
    path('admin/backup/create/', views.admin_backup_create, name='admin_backup_create'),
    path('admin/backup/<str:backup_filename>/restore/', views.admin_backup_restore, name='admin_backup_restore'),
    path('admin/backup/<str:backup_filename>/delete/', views.admin_backup_delete, name='admin_backup_delete'),
]
```

## 8. 视图函数与模板设计

### 8.1 核心视图函数

#### 8.1.1 账号管理视图

| 视图函数名 | URL路径 | 功能描述 | 权限控制 | 模板文件 |
|----------|--------|---------|---------|----------|
| `dashboard` | `/` | 用户仪表盘 | 所有登录用户 | templates/dashboard.html |
| `login_view` | `/accounts/login/` | 用户登录 | 匿名用户 | templates/accounts/login.html |
| `logout_view` | `/accounts/logout/` | 用户登出 | 登录用户 | 重定向到登录页 |
| `register_view` | `/accounts/register/` | 教师注册 | 匿名用户 | templates/accounts/register.html |
| `profile_view` | `/accounts/profile/` | 查看个人资料 | 登录用户 | templates/accounts/profile.html |
| `profile_edit_view` | `/accounts/profile/edit/` | 编辑个人资料 | 登录用户 | templates/accounts/profile_edit.html |
| `admin_teacher_list` | `/accounts/admin/teachers/` | 教师列表 | 管理员 | templates/accounts/admin/teacher_list.html |
| `admin_teacher_edit` | `/accounts/admin/teachers/<id>/edit/` | 编辑教师信息 | 管理员 | templates/accounts/admin/teacher_edit.html |
| `admin_teacher_toggle` | `/accounts/admin/teachers/<id>/toggle/` | 启用/禁用教师 | 管理员 | 重定向到教师列表 |
| `admin_admin_list` | `/accounts/admin/admins/` | 管理员列表 | 超级管理员 | templates/accounts/admin/admin_list.html |

#### 8.1.2 订单管理视图

| 视图函数名 | URL路径 | 功能描述 | 权限控制 | 模板文件 |
|----------|--------|---------|---------|----------|
| `admin_order_list` | `/orders/admin/orders/` | 订单列表(管理员) | 管理员 | templates/orders/admin/order_list.html |
| `admin_order_create` | `/orders/admin/orders/create/` | 创建订单 | 管理员 | templates/orders/admin/order_create.html |
| `admin_order_edit` | `/orders/admin/orders/<id>/edit/` | 编辑订单 | 管理员 | templates/orders/admin/order_edit.html |
| `teacher_order_list` | `/orders/teacher/orders/` | 订单列表(教师) | 教师 | templates/orders/teacher/order_list.html |
| `teacher_order_update_status` | `/orders/teacher/orders/<id>/update-status/` | 更新订单状态 | 教师 | 重定向到订单详情 |
| `salary_application_list` | `/orders/applications/` | 工资申请列表(管理员) | 管理员 | templates/orders/application_list.html |
| `teacher_salary_application_create` | `/orders/teacher/applications/create/` | 创建工资申请 | 教师 | templates/orders/teacher/application_create.html |
| `salary_application_approve` | `/orders/applications/<id>/approve/` | 批准工资申请 | 管理员 | 重定向到申请列表 |
| `admin_log_list` | `/orders/admin/logs/` | 操作日志列表 | 管理员 | templates/orders/admin/log_list.html |
| `admin_backup_list` | `/orders/admin/backup/` | 备份管理列表 | 管理员 | templates/orders/admin/backup_list.html |

### 8.2 模板设计

#### 8.2.1 基础模板 (base.html)
基础模板定义了网站的整体结构，包括导航栏、侧边栏和页脚。所有其他模板都继承自这个基础模板，确保网站风格一致。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}课程进度管理系统{% endblock %}</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <!-- 自定义CSS -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'dashboard' %}">课程进度管理系统</a>
            <!-- 导航链接和用户信息 -->
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- 侧边栏 -->
            <aside class="col-md-3 col-lg-2 bg-light sidebar">
                {% include 'sidebar.html' %}
            </aside>

            <!-- 主内容区域 -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <!-- 页脚 -->
    <footer class="bg-light text-center text-lg-start mt-auto">
        <div class="container p-4">
            <p>课程进度管理系统 - 阮老师个人学习项目</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- 自定义JS -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 8.2.2 仪表盘模板 (dashboard.html)
仪表盘模板展示用户的核心信息和常用功能入口，根据用户角色显示不同的内容。

#### 8.2.3 表单模板设计
系统中的表单设计遵循Bootstrap的表单样式，确保良好的用户体验和数据验证。关键表单包括：

- 登录表单：用户名和密码字段
- 注册表单：个人信息和账户设置字段
- 订单表单：订单详情和教师分配字段
- 工资申请表单：申请金额和证明材料上传字段

## 9. 权限控制与安全

### 9.1 角色权限系统

| 角色 | 权限描述 | 页面访问权限 |
|-----|---------|------------|
| 超级管理员 | 系统最高权限 | 所有功能页面 |
| 普通管理员 | 管理教师和订单 | 教师管理、订单管理、工资申请审核、日志查看、数据备份 |
| 教师 | 管理个人订单和工资申请 | 个人资料、分配的订单管理、工资申请提交和查看 |

### 9.2 权限控制实现

系统使用自定义的权限装饰器来控制视图函数的访问权限：

```python
# accounts/decorators.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps

def role_required(roles):
    """检查用户是否具有指定角色之一"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if request.user.role not in roles:
                return HttpResponseForbidden("您没有权限访问此页面")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
```

使用示例：
```python
@login_required
@role_required(['super_admin', 'admin'])
def admin_order_list(request):
    # 管理员订单列表视图
    pass
```

### 9.3 安全措施

1. **密码安全**：
   - 使用Django的密码哈希系统
   - 密码复杂度验证

2. **数据验证**：
   - 表单数据验证
   - URL参数验证
   - 防止SQL注入和XSS攻击

3. **CSRF保护**：
   - Django的CSRF令牌机制
   - 表单提交的CSRF验证

4. **操作日志**：
   - 记录所有关键操作
   - 包含操作用户、时间、IP地址等信息

5. **数据备份**：
   - 自动备份机制
   - 手动备份功能
   - 备份文件管理

6. **会话管理**：
   - 会话超时设置
   - 安全的会话存储

## 10. 系统配置与部署

### 10.1 开发环境配置

#### 10.1.1 环境变量配置 (.env)
```
# 项目密钥（生产环境必须修改）
SECRET_KEY=django-insecure-#c)(jlhd5z_%7yvy6kld@892%bv@3-9or-64%)5w(@%v=r1u+8

# 调试模式（生产环境设置为False）
DEBUG=True

# 允许的主机（生产环境设置为实际域名）
ALLOWED_HOSTS=127.0.0.1,localhost
```

#### 10.1.2 Django设置 (settings.py)
关键配置项：
- `INSTALLED_APPS`：安装的应用列表
- `DATABASES`：数据库配置
- `AUTH_USER_MODEL`：自定义用户模型
- `STATIC_URL`/`STATIC_ROOT`：静态文件配置
- `MEDIA_URL`/`MEDIA_ROOT`：媒体文件配置
- `LOGIN_URL`/`LOGIN_REDIRECT_URL`：登录相关配置

### 10.2 生产环境部署

#### 10.2.1 部署架构
- **Web服务器**：Nginx
- **应用服务器**：Gunicorn
- **数据库**：PostgreSQL
- **操作系统**：Ubuntu 20.04 LTS

#### 10.2.2 部署步骤

1. **安装依赖**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
   ```

2. **创建项目目录**
   ```bash
   sudo mkdir -p /var/www/class_os
   sudo chown -R your_user:www-data /var/www/class_os
   ```

3. **克隆项目**
   ```bash
   cd /var/www/class_os
   git clone <项目仓库地址> .
   ```

4. **创建虚拟环境并安装依赖**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **配置PostgreSQL数据库**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE class_os_db;
   CREATE USER class_os_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE class_os_user SET client_encoding TO 'utf8';
   ALTER ROLE class_os_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE class_os_user SET timezone TO 'Asia/Shanghai';
   GRANT ALL PRIVILEGES ON DATABASE class_os_db TO class_os_user;
   \q
   ```

6. **配置项目设置**
   ```python
   # 修改settings.py
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': 'class_os_db',
           'USER': 'class_os_user',
           'PASSWORD': 'your_secure_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   
   # 静态文件设置
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ```

7. **运行迁移和收集静态文件**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

8. **创建Gunicorn服务**
   ```bash
   sudo nano /etc/systemd/system/gunicorn.service
   ```

   内容：
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target
   
   [Service]
   User=your_user
   Group=www-data
   WorkingDirectory=/var/www/class_os
   ExecStart=/var/www/class_os/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/class_os/class_os.sock class_os.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

9. **配置Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/class_os
   ```

   内容：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /var/www/class_os;
       }
       
       location /media/ {
           root /var/www/class_os;
       }
       
       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/class_os/class_os.sock;
       }
   }
   ```

10. **启动服务**
    ```bash
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn
    sudo ln -s /etc/nginx/sites-available/class_os /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## 11. 维护与更新

### 11.1 日常维护

1. **数据备份检查**
   - 定期检查自动备份是否正常工作
   - 验证备份文件的完整性

2. **日志审查**
   - 定期查看操作日志，检查异常行为
   - 监控服务器日志，及时发现问题

3. **性能监控**
   - 监控系统响应时间和资源使用情况
   - 根据需要进行性能优化

### 11.2 系统更新

1. **代码更新**
   ```bash
   cd /var/www/class_os
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   sudo systemctl restart gunicorn
   ```

2. **依赖更新**
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

### 11.3 常见问题排查

1. **页面访问错误**
   - 检查用户权限设置
   - 查看Django日志和Nginx错误日志
   - 验证URL路径和视图函数是否匹配

2. **数据库连接问题**
   - 检查数据库配置是否正确
   - 验证数据库服务是否运行
   - 检查数据库用户权限

3. **静态文件无法访问**
   - 确认已运行`collectstatic`命令
   - 检查Nginx配置中的静态文件路径
   - 验证静态文件权限

4. **上传文件问题**
   - 检查文件大小限制设置
   - 验证上传目录权限
   - 检查媒体文件配置

## 12. 扩展与定制

### 12.1 添加新功能

1. **创建新的应用**
   ```bash
   python manage.py startapp new_app
   ```

2. **注册应用**
   在`settings.py`的`INSTALLED_APPS`中添加新应用

3. **定义数据模型**
   在新应用的`models.py`中定义数据模型

4. **创建视图和模板**
   实现业务逻辑和用户界面

5. **配置URL路由**
   在项目的`urls.py`中添加新应用的URL配置

### 12.2 定制化配置

1. **主题定制**
   - 修改`static/css/main.css`文件调整样式
   - 在`base.html`中添加自定义CSS变量

2. **功能开关**
   - 在`settings.py`中添加功能开关配置
   - 使用条件判断控制功能显示

3. **集成第三方服务**
   - 邮件服务：配置SMTP发送通知
   - 支付服务：集成支付API
   - 短信服务：集成短信验证码

## 13. 测试与质量保障

### 13.1 测试策略

1. **单元测试**
   - 测试数据模型的业务逻辑
   - 测试视图函数的响应
   - 测试表单验证和处理

2. **集成测试**
   - 测试功能模块之间的交互
   - 测试数据库操作的完整性

3. **用户测试**
   - 不同角色的用户体验测试
   - 关键业务流程的端到端测试

### 13.2 测试执行

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test accounts
python manage.py test orders

# 运行特定测试用例
python manage.py test accounts.tests.TestUserAuthentication
```

### 13.3 代码质量

1. **代码风格检查**
   - 使用Black或Flake8检查代码风格
   - 遵循PEP 8编码规范

2. **代码复杂度管理**
   - 定期重构复杂代码
   - 使用函数和类封装功能模块

## 14. 项目文档

### 14.1 开发文档
- **API文档**：系统API接口说明
- **数据库设计文档**：数据模型和关系图
- **用户手册**：系统使用指南

### 14.2 用户文档
- **管理员手册**：管理员功能操作指南
- **教师手册**：教师功能使用说明
- **快速入门**：新用户快速上手指南

## 15. 总结与未来规划

### 15.1 项目总结
Class_os（课程进度管理系统）是一个功能完善的教育机构管理系统，它解决了教育机构在订单管理、教师管理和工资申请流程中的痛点问题。系统采用现代化的技术栈和架构设计，具有良好的可扩展性和维护性。

### 15.2 未来规划

1. **功能增强**
   - 学生管理模块：增加学生信息和学习进度管理
   - 课程管理模块：添加课程设置和教学计划功能
   - 报表分析模块：增强数据统计和可视化功能

2. **技术升级**
   - 前后端分离：采用Vue.js/React重构前端
   - API接口优化：完善RESTful API设计
   - 缓存优化：增加Redis缓存支持

3. **性能改进**
   - 数据库优化：索引优化和查询优化
   - 代码优化：减少响应时间和资源消耗
   - 负载均衡：支持多服务器部署

4. **用户体验提升**
   - 移动端应用：开发iOS和Android应用
   - 响应式设计优化：提升移动端体验
   - 无障碍访问：支持无障碍功能

通过持续的改进和优化，Class_os系统将更好地服务于教育机构，提高管理效率，促进教育资源的有效利用。