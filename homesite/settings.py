import importlib.util
import locale
import os
import sys
from pathlib import Path

os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

DATA_DIR = Path('~/homesite-data').expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_DIR = DATA_DIR / 'private'
PRIVATE_DIR.mkdir(exist_ok=True)
TMP_DIR = DATA_DIR / 'temp'
TMP_DIR.mkdir(exist_ok=True)

FILE_UPLOAD_TEMP_DIR = TMP_DIR
FILE_UPLOAD_PERMISSIONS = 0o644

DEBUG = False
DEBUG_TOOLBAR = False

ADMINS = (
    ('Admin', 'admin@server.com'),
)
MANAGERS = ADMINS

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

ALLOWED_HOSTS = ['*']
X_FRAME_OPTIONS = 'SAMEORIGIN'

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

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = DATA_DIR / 'media'

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
STATIC_DIR = DATA_DIR / 'static'  # this var is not used by Django
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

TEMPLATES = [
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'homesite.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',  # disabled because no database is used
    'django.contrib.messages',
    # 'django.contrib.admin',  # disabled because no database is used
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django_web_utils.file_browser',
    'django_web_utils.monitoring',
    'homesite.base',
]

AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    # 'django.contrib.auth.backends.RemoteUserBackend',
    'homesite.backend.SettingsBackend',
)

# Logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            '()': 'django.utils.log.ServerFormatter',
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
            'filename': TMP_DIR / 'django.log',
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
SESSION_COOKIE_AGE = 12 * 3600  # in seconds
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = TMP_DIR
CSRF_COOKIE_SECURE = True

# Auth config
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
AUTHENTICATION_USERS = {
    # 'admin': {'is_active': True, 'is_staff': False, 'is_superuser': False, 'password': 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='}
}

# File browser config
FB_PUBLIC_ROOT = DATA_DIR / 'public'
FB_PUBLIC_ROOT.mkdir(exist_ok=True)
FB_PROTECTED_ROOT = DATA_DIR / 'protected'
FB_PROTECTED_ROOT.mkdir(exist_ok=True)
FILE_BROWSER_BASE_TEMPLATE = 'base/storage.html'
FILE_BROWSER_DIRS = {
    'fb-public': (FB_PUBLIC_ROOT, '/public/'),
    'fb-protected': (FB_PROTECTED_ROOT, '/protected/'),
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

# Import local settings
# ---------------------
OVERRIDE_PATH = PRIVATE_DIR / 'settings_override.py'
if OVERRIDE_PATH.exists():
    spec = importlib.util.spec_from_file_location('settings_override', OVERRIDE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules['settings_override'] = mod
    from settings_override import *  # NOQA: F401,F403

# Apply changes depending on local settings
# -----------------------------------------
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if DEBUG_TOOLBAR:
    DEBUG = True
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    if 'INTERNAL_IPS' not in globals():
        INTERNAL_IPS = '127.0.0.1'
elif os.environ.get('DEBUG'):
    DEBUG = os.environ['DEBUG'] == 'on'
if DEBUG:
    TEMPLATES[0]['OPTIONS']['debug'] = True
    TEMPLATES[0]['OPTIONS']['string_if_invalid'] = 'Invalid template string: "%s"'
    LOGGING['root']['level'] = 'DEBUG'
    LOGGING['root']['handlers'] = ['console']
    del LOGGING['loggers']['django.request']['handlers']
    import warnings
    warnings.simplefilter('always')
    warnings.simplefilter('ignore', ResourceWarning)  # Hide unclosed files warnings
    os.environ['PYTHONWARNINGS'] = 'always'  # Also affect subprocesses
else:
    import logging
    logging.captureWarnings(False)

# Disable logging config for daemons
if os.environ.get('DJANGO_LOGGING') == 'none':
    LOGGING_CONFIG = None
