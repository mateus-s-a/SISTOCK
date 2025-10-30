"""
ASGI config for sistock project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Define o módulo de settings baseado na variável ENV
env = os.environ.get('ENV', 'development').lower()

if env == 'production':
    settings_module = 'sistock.settings.production'
elif env == 'development':
    settings_module = 'sistock.settings.development'
else:
    settings_module = 'sistock.settings.development'  # Fallback para development

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistock.settings')

application = get_asgi_application()
