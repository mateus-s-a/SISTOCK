from .base import *
from decouple import config
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# ALLOWED_HOSTS deve ser configurado via variável de ambiente
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [h.strip() for h in v.split(',')] if v else [],
    default=''
)


# Database para produção (PostgreSQL)
# Mantém SQLite como fallback, mas permite PostgreSQL via DATABASE_URL
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default={
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        cast=lambda v: {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': v.split('/')[-1],
            'USER': v.split('@')[0].split(':')[1].split('//')[1],
            'PASSWORD': v.split('@')[0].split(':')[2],
            'HOST': v.split('@')[1].split(':')[0],
            'PORT': v.split('@')[1].split(':')[1].split('/')[0],
        } if v.startswith('postgresql://') else {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    )
}


# Security Settings para Produção
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_REFERRER_POLICY = config('SECURE_REFERRER_POLICY', default='same-origin')

# Session e Cookie Security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)  # 24 horas

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool)

# X-Frame-Options
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='DENY')

# Static files para produção
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise para servir arquivos estáticos em produção
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files para produção
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email backend para produção
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sistock.com')

# Logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'sistock.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'sistock': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Cache para produção (Redis recomendado)
CACHES = {
    'default': {
        'BACKEND': config(
            'CACHE_BACKEND',
            default='django.core.cache.backends.locmem.LocMemCache'
        ),
        'LOCATION': config('CACHE_LOCATION', default=''),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        } if config('CACHE_BACKEND', default='').startswith('django_redis') else {},
    }
}


# Configurações adicionais para diferentes provedores de deploy
# Heroku
if 'DYNO' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Railway
if 'RAILWAY_ENVIRONMENT' in os.environ:
    ALLOWED_HOSTS.append(config('RAILWAY_PUBLIC_DOMAIN', default=''))

# PythonAnywhere
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    ALLOWED_HOSTS.append(config('PYTHONANYWHERE_DOMAIN', default=''))