"""
Django settings for DigiCorderServer project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bpx%t#w_(^_h0yt#xqbit0(p%9!5bctf2ai4@-kryin+x0%=@5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

MEDIA_ROOT = ''
MEDIA_URL = '/media/AutoRecorder/'

if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'AutoRecorder', 'media', 'AutoRecorder')
else:
    MEDIA_ROOT = '/some/absolute/path/on/production/server'

print(MEDIA_ROOT)

LOGGING = {
    'version': 1,                       # the dictConfig format version
    'disable_existing_loggers': False,  # retain the default loggers
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {threadName:s} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message} {threadName:s} {module}',
            'style': '{',
        }
    },
    'handlers': {
        'projectRootFile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'server.log',
            'maxBytes': 1048576*5,
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'AutoRecorder.consumers': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'AutoRecorder.apps': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'AutoRecorder.signals': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'AutoRecorder.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'AutoRecorder.tests': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },                
    }
}


ALLOWED_HOSTS = ['192.168.178.181','172.20.10.13', '172.16.30.220', 'localhost', '127.0.0.1', '192.168.10.11', '[::1]']


# Application definition

INSTALLED_APPS = [
    'channels',
    'AutoRecorder.apps.AutoRecorderConfig',
    'polls.apps.PollsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'register.apps.RegisterConfig',
    'django_cleanup.apps.CleanupConfig',
]

ASGI_APPLICATION = 'DigiCorderServer.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DigiCorderServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#WSGI_APPLICATION = 'DigiCorderServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'AutoRecorder',
        'USER': 'AutoRecorder',
        'PASSWORD': 'AutoRecorder',
        'HOST': 'localhost',
        'PORT': '5432',
        # 'OPTIONS': {
        #     'service': 'postgres',
        #     'passfile': '.my_pgpass',
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK="bootstrap5"
CRISPY_FAIL_SILENTLY = not DEBUG

LOGIN_REDIRECT_URL = "/AutoRecorder"
LOGOUT_REDIRECT_URL = "/AutoRecorder"


#PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
# STATICFILES_DIRS = [
#     BASE_DIR / "static"
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
