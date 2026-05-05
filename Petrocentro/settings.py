"""
Django settings for Petrocentro project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-r9%9vu)tf(0r_k-!z84&b_1kuhpk8rm)18le5(l)7*f54c^wiu') # ¡IMPORTANTE! Usar variable de entorno en producción

# SECURITY WARNING: don't run with debug turned on in production!
# Por defecto True para desarrollo local. En producción se debe cambiar a False.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True' # En producción, debe ser False


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') # Configurar dominios de producción


# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'paginaPetrocentro',
    'django_summernote',
    'blogs',
    'configuracion',
    'django.contrib.sitemaps',

    # 'channels_redis', # Descomentar y configurar para Channel Layers en producción (pip install channels_redis)
]
PASSWORD_RESET_TIMEOUT_DAYS = 1 


PASSWORD_RESET_TEMPLATES = {
    'password_reset_form': 'paginaPetrocentro/registration/password_reset_form.html',
    'password_reset_done': 'paginaPetrocentro/registration/password_reset_done.html',
    'password_reset_confirm': 'paginaPetrocentro/registration/password_reset_confirm.html',
    'password_reset_complete': 'paginaPetrocentro/registration/password_reset_complete.html',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Petrocentro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'users', 'templates'), # Única fuente de verdad explícita
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.notificaciones_empleado', # Nuevo procesador
            ],
        },
    },
]
SUMMERNOTE_CONFIG = {
    
    'summernote': {
        'width': '100%',
        'height': '480',      
        'styleTags': ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    }
}
# Duración de la sesión (en segundos)
SESSION_COOKIE_AGE = 1209600  # 2 semanas

# Hacer que la sesión expire cuando el navegador se cierre
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Usar solo cookies seguras para la sesión
# Se activan automáticamente solo si DEBUG es False (Producción)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = ['https://petrocentro.co', 'https://www.petrocentro.co']


WSGI_APPLICATION = 'Petrocentro.wsgi.application'


# Configuración de Channels y Chat (para WebSockets)
ASGI_APPLICATION = 'Petrocentro.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # En producción, se recomienda usar un backend basado en Redis para Channel Layers.
        # Para usarlo, descomentar 'channels_redis' en INSTALLED_APPS y esta configuración:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')], # Usar variable de entorno para la URL de Redis
        # },
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'petrocentro'),
        'USER': os.environ.get('DB_USER', 'petrocentro_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'petrocentro@2026'), # ¡IMPORTANTE! Usar variable de entorno en producción
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3307'),
        'OPTIONS': {
            'ssl': {'disabled': True},
        },
    }
}







# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True # Siempre True para SMTP seguro
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'ti.petrocentro@gmail.com') # ¡IMPORTANTE! Usar variable de entorno en producción
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'zcqu ujkp hinr dlck') # ¡IMPORTANTE! Usar variable de entorno en producción

DOMAIN_NAME = os.environ.get('DJANGO_DOMAIN_NAME', 'http://127.0.0.1:8000') # Configurar dominio de producción
DEFAULT_FROM_EMAIL = 'ti.petrocentro@gmail.com'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración moderna de almacenamiento (Django 4.2+)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = '/login_view/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
'version': 1,
'disable_existing_loggers': False,
'handlers': {
'file': {
'level': 'ERROR',
'class': 'logging.FileHandler', 
'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
},
},
'loggers':{
'django':{
'handlers':['file'],
'level': 'ERROR',
'propagate': True,
},
},
}

# Configuración de Google reCAPTCHA v2
RECAPTCHA_PUBLIC_KEY = '6LfOTNksAAAAAHq5Np-82UxctfY2GYcroJsI7V4A'
RECAPTCHA_PRIVATE_KEY = '6LfOTNksAAAAAG9RBYAn9VXaUfmb4QkbVzNyKMHz'
