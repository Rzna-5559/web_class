"""
WSGI config for class_os project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# 仅在PythonAnywhere环境中添加项目路径和激活虚拟环境
if os.path.exists('/home/rznar'):
    # PythonAnywhere环境
    sys.path.append('/home/rznar/mysite')
    sys.path.append('/home/rznar/mysite/class_os')
    
    # 激活虚拟环境
    activate_this = '/home/rznar/.virtualenvs/mysite/bin/activate_this.py'
    if os.path.exists(activate_this):
        exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
from django.conf import settings

# 设置Django环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "class_os.settings")

application = get_wsgi_application()

# 配置静态文件和媒体文件的处理
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(application)