from pathlib import Path
from dotenv import dotenv_values
import os

config = dotenv_values('.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.get('SECRET_KEY', 'secret')

CELERY_BROKER_URL = config.get('CELERY_BROKER_URL', 'amqp://rabbit:5672/')

AWS = {
    'AWS_ACCESS_KEY_ID': config.get('AWS_ACCESS_KEY_ID', 'temp'),
    'AWS_SECRET_ACCESS_KEY': config.get('AWS_SECRET_ACCESS_KEY', 'temp'),
    'AWS_DEFAULT_REGION': config.get('AWS_DEFAULT_REGION', 'us-east-1'),
    'AWS_ENDPOINT_URL': config.get('AWS_ENDPOINT_URL', 'http://localstack:4566/'),
    'AWS_EMAIL_SOURCE': config.get('AWS_EMAIL_SOURCE', 'email@gmail.com'),
    'AWS_BUCKET_NAME': config.get('AWS_BUCKET_NAME', 'bucket'),
}

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'pages',
    'posts',

    'rest_framework',
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Innotter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Innotter.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.get('POSTGRES_NAME', 'postgres'),
        'USER': config.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': config.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': config.get('POSTGRES_HOST', 'db'),
        'PORT': config.get('POSTGRES_PORT', 5432)
    }
}

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

AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Minsk'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'EXCEPTION_HANDLER': 'Innotter.exceptions.core_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.backends.JWTAuthentication',
    ]
}

#DEBUG TOOLBAR
INTERNAL_IPS = [
    '127.0.0.1',
]

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
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
