"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')

# Get the WSGI application for the Django project
application = get_wsgi_application()
