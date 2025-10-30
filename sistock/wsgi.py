"""
WSGI config for sistock project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Define o módulo de settings baseado na variável ENV
env = os.environ.get('ENV', 'development').lower()

if env == 'production':
    settings_module = 'sistock.settings.production'
elif env == 'development':
    settings_module = 'sistock.settings.development'
else:
    settings_module = 'sistock.settings.development'  # Fallback para development

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistock.settings')

application = get_wsgi_application()
