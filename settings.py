#!/usr/bin/python3
# -*- coding: utf-8 -*-
import imp
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
if os.path.dirname(BASE_DIR) not in sys.path:
    sys.path.append(os.path.dirname(BASE_DIR))
LOGS_DIR = os.path.join(BASE_DIR, 'temp')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

DEBUG = False
DEBUG_TOOLBAR = False

ADMINS = (
    ('Admin', 'admin@server.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

ALLOWED_HOSTS = '*'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('fr', 'Français'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'http://media.lawrence.com', 'http://example.com/media/'
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATIC_DIR = os.path.join(BASE_DIR, 'static')  # this var is not used by Django
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_DIR,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    # 'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'T^_r4$hlo9c$_*u7xj)_x$2%+5Tb#-5%+bf&4(%o_@!bF=$1m_'

TEMPLATES = (
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                # 'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # 'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            )
        },
    },
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'homesite.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django_web_utils.file_browser',
    'django_web_utils.monitoring',
    'homesite.base',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    # 'django.contrib.auth.backends.RemoteUserBackend',
)

# Logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(module)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'django_log_file': {
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['django_log_file'],
        'level': 'INFO',
        'propagate': False,
    },
}

# Session config
SESSION_COOKIE_NAME = 'hssessionid'
# SESSION_COOKIE_AGE = 3600 # in seconds
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Auth config
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# File browser config
FB_PUBLIC_ROOT = os.path.join(BASE_DIR, 'hosting-public')
if not os.path.exists(FB_PUBLIC_ROOT):
    os.makedirs(FB_PUBLIC_ROOT)
FB_PRIVATE_ROOT = os.path.join(BASE_DIR, 'hosting-private')
if not os.path.exists(FB_PRIVATE_ROOT):
    os.makedirs(FB_PRIVATE_ROOT)
FILE_BROWSER_BASE_TEMPLATE = 'base/storage.html'
FILE_BROWSER_DIRS = {
    'fb-public': (FB_PUBLIC_ROOT, '/storage/public/'),
    'fb-private': (FB_PRIVATE_ROOT, '/storage/private/'),
}

# Munin
MUNIN_DIR = '/var/cache/munin/www'
MUNIN_BASE = 'localdomain/localhost.localdomain/index.html'
MUNIN_SCRIPTS_DIR = '/usr/lib/munin/cgi'

# Daemons monitoring config (from django web utils)
MONITORING_DAEMONS_INFO = 'homesite.base.daemons'
MONITORING_BASE_TEMPLATE = 'base/monitoring.html'
MONITORING_TEMPLATE_DATA = dict(section='monitoring')

# Email config
SERVER_EMAIL = 'server@host.com'  # Used as sender for error emails
DEFAULT_FROM_EMAIL = 'server@host.com'   # Used as sender for other emails
EMAIL_USE_TLS = False
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25

# Import instance settings
# -------------------------------------------------------------------------------
override_path = os.path.join(BASE_DIR, 'settings_override.py')
if os.path.exists(override_path):
    override = imp.load_source('settings_override', override_path)
    for key in dir(override):
        if not key.startswith('_'):
            globals()[key] = getattr(override, key)

# Apply changes depending on instance config
# -------------------------------------------------------------------------------
if DEBUG:
    TEMPLATES[0]['OPTIONS']['debug'] = True
    TEMPLATES[0]['OPTIONS']['string_if_invalid'] = 'Invalid template string: "%s"'
    LOGGING['root']['level'] = 'DEBUG'
    LOGGING['root']['handlers'] = ['console']
else:
    import logging
    logging.captureWarnings(False)
# Debug toolbar
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': '/static/jquery/jquery-latest.min.js'}

# Disable logging config for daemons
if os.environ.get('DJANGO_LOGGING') == 'none':
    LOGGING_CONFIG = None
