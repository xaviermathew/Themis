"""
Django settings for themis project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import warnings
from kombu import Exchange, Queue

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(c94hapg+c&$67jaol62+c+*q-74)lt(f!%3kiy)c1f#b81b^-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
PROJECT_APPS = [
    'themis.core',
    'themis.entity',
    'themis.news',
]
THIRD_PARTY_APPS = [
    'rest_framework'
]
INSTALLED_APPS = PROJECT_APPS + [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'themis.core.urls'

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

WSGI_APPLICATION = 'themis.core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'themis',
        'USER': 'themis',
        'PASSWORD': 'themis',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
LOG_FOLDER = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILENAME = os.path.join(LOG_FOLDER, 'themis.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)s] %(message)s"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'elasticsearch': {
            'level': 'INFO',
            'propagate': False,
        },
        'urllib3.util.retry': {
            'level': 'INFO',
            'propagate': False,
        },
        'asyncio': {
            'level': 'INFO',
            'propagate': False,
        },
        'parso': {
            'level': 'INFO',
            'propagate': False,
        },
    },
}

import logging

logging.getLogger('parso').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)


# celery
# https://www.cloudamqp.com/docs/celery.html
CELERY_BROKER_URL = None
CELERY_BROKER_POOL_LIMIT = 1 # Will decrease connection usage
CELERY_BROKER_HEARTBEAT = None # We're using TCP keep-alive instead
CELERY_BROKER_CONNECTION_TIMEOUT = 30 # May require a long timeout due to Linux DNS timeouts etc
CELERY_RESULT_BACKEND = None # AMQP is not recommended as result backend as it creates thousands of queues
CELERY_EVENT_QUEUE_EXPIRES = 60 # Will delete all celeryev. queues without consumers after 1 minute.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1 # Disable prefetching, it's causes problems and doesn't help performance
CELERY_IGNORE_RESULT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_QUEUE_DEFAULT = 'T_default'
CELERY_TASK_ROUTING_KEY_DEFAULT = 'themis.T_default'

CELERY_TASK_QUEUE_CRAWL_FEED = 'T_crawl_feed'
CELERY_TASK_ROUTING_KEY_CRAWL_FEED = 'themis.T_crawl_feed'

CELERY_TASK_QUEUE_PROCESS_ARTICLE = 'T_process_article'
CELERY_TASK_ROUTING_KEY_PROCESS_ARTICLE = 'themis.T_process_article'

CELERY_TASK_QUEUE_CRAWL_TWITTER = 'T_crawl_twitter'
CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER = 'themis.T_crawl_twitter'

CELERY_TASK_QUEUE_PROCESS_TWEET = 'T_process_tweet'
CELERY_TASK_ROUTING_KEY_PROCESS_TWEET = 'themis.T_process_tweet'

CELERY_TASK_QUEUES = (
    Queue(CELERY_TASK_QUEUE_DEFAULT,
          Exchange(CELERY_TASK_QUEUE_DEFAULT),
          routing_key=CELERY_TASK_ROUTING_KEY_DEFAULT),
    Queue(CELERY_TASK_QUEUE_CRAWL_FEED,
          Exchange(CELERY_TASK_QUEUE_CRAWL_FEED),
          routing_key=CELERY_TASK_ROUTING_KEY_CRAWL_FEED),
    Queue(CELERY_TASK_QUEUE_PROCESS_ARTICLE,
          Exchange(CELERY_TASK_QUEUE_PROCESS_ARTICLE),
          routing_key=CELERY_TASK_ROUTING_KEY_PROCESS_ARTICLE),
    Queue(CELERY_TASK_QUEUE_CRAWL_TWITTER,
          Exchange(CELERY_TASK_QUEUE_CRAWL_TWITTER),
          routing_key=CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER),
    Queue(CELERY_TASK_QUEUE_PROCESS_TWEET,
          Exchange(CELERY_TASK_QUEUE_PROCESS_TWEET),
          routing_key=CELERY_TASK_ROUTING_KEY_PROCESS_TWEET),
)


# ES
ELASTICSEARCH_HOSTS = ['localhost:9200']


for app in PROJECT_APPS:
    try:
        exec("from {}.app_settings import *".format(app))
        print("Imported {}.app_settings".format(app))
    except ImportError as ex:
        warnings.warn("Importing {}.app_settings.py failed - ({})".format(app, ex))

try:
    from .local import *
except ImportError:
    warnings.warn('local.py is missing')
