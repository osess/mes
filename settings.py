# -*- coding: utf-8 -*-
# Django settings for basic pinax project.


VERSION = 0.27

import sys
import os.path
import posixpath
from datetime import date


terminal_date = date(2016, 7, 1)

#Enable plaintext password and save it in person.UserPlainPassword
ENABLE_PLAIN_PASSWORD = True


MAX_UPLOAD_SIZE = 55555555555

REMEMBER = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_EXPIRE_AFTER = 1800
SESSION_SECURITY_WARN_AFTER = 1800

DATE_FORMAT = 'Y/m/d'
DATETIME_FORMAT = 'Y/m/d H:m'
CAN_ADD_SUPER_USER = False

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
THIRD_PARTY_ROOT = os.path.join(PROJECT_ROOT,"thirdparty")
THEME_ROOT          = os.path.join(PROJECT_ROOT,"theme")

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

# django-compressor is turned off by default due to deployment overhead for
# most users. See <URL> for more information
COMPRESS = False

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "dev.db",                       # Or path to database file if using sqlite3.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}
DATABASE_ENGINE = 'sqlite3'
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Asia/Shanghai"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "zh-CN"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
UPLOAD_ROOT = '/data/mes/upload/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"
UPLOAD_URL = "/site_media/upload/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/"
#STATIC_URL = "/static/"

ACCOUNT_OPEN_SIGNUP = 0

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
    os.path.join(PROJECT_ROOT, "site_media"),
]

STATICFILES_FINDERS = [
    "staticfiles.finders.FileSystemFinder",
    "staticfiles.finders.AppDirectoriesFinder",
    "staticfiles.finders.LegacyAppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Subdirectory of COMPRESS_ROOT to store the cached media files in
COMPRESS_OUTPUT_DIR = "cache"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "!rcg%bqf27w8*42-#z_+r+hg7rp9=xtge^gkd0nv#i=t@w1r&@"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    #"django.template.loaders.filesystem.load_template_source",
    #"django.template.loaders.app_directories.load_template_source",
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    #"django.middleware.csrf.CsrfResponseMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "session_security.middleware.SessionSecurityMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    #"pinax.apps.account.middleware.LocaleMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    # "django_pdb.middleware.PdbMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
    '.',
]

CONTACT_EMAIL = "info@octopusinfo.com"

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    
    "staticfiles.context_processors.static",
    
    "pinax.core.context_processors.pinax_settings",
    
    "pinax.apps.account.context_processors.account",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "serv.context_processors.start",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.comments",
    # "django.contrib.staticfiles",
    
    "pinax.templatetags",
    
    # theme
    #"pinax_theme_bootstrap",
    "201504",
    
    # external
    "notification", # must be first
    "staticfiles",
    "compressor",
    # "debug_toolbar",
    "mailer",
    "django_openid",
    "timezones",
    "emailconfirmation",
    "announcements",
    "pagination",
    "idios",
    "metron",
    
    #xadmin
    "xadmin",
    "crispy_forms",
    "reversion",
    # Pinax
    "pinax.apps.account",
    "pinax.apps.signup_codes",
    
    # project
    "about",
    "profiles",
    #"avatar",
    "blog",

    # by xxd
    "tastypie",
    "person",
    "customer",
    "companydepartment",
    "permissions",
    "workflows",
    "technologies",
    "yt_file",
    "yt_timesheet",
    "yt_log",
    "warehouse",
    "productcatalog",
    "xlrd",
    "reportlab",
    "trml2pdf",
    "PyPDF2",
    "yt_report",
    # "django_pdb",
    #"app",
    "actstream",
    "yt_actstream",
    "session_security",
    

    'qhonuskan_votes',
    'djangovoice',

    #by lxy
    "django_messages",
    "maintenance",
    "hubarcode",
    "yt_barcode",
    "yt_object",
    "device",
    "material",
    "quality",
    "manufactureplan",
    "report",
    "redis",
    "constance",
    "picklefield",
    "constance.backends.database",
    'django_extensions',
]


ACTSTREAM_SETTINGS = {
    'MODELS': ('yt_actstream.Player', 'auth.user', 'auth.group'),
    'MANAGER': 'actstream.managers.ActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': False,
    'GFK_FETCH_DEPTH': 0,
}

CONSTANCE_CONFIG = {
    'MY_SETTINGS_KEY': (42, 'the answer to everything'),
    'TEST': (6, 'TEST'),
    'FLOW_NUMBER': (1, 'flow number used in plan report'),
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

#django.db.backends.sqlite3

CONSTANCE_REDIS_CONNECTION = {
    'host': 'localhost',
    'port': 8080,
    'db': 0,
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

EMAIL_BACKEND = "mailer.backend.DbBackend"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

AUTHENTICATION_BACKENDS = [
    "pinax.apps.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/account/login/" # @@@ any way this can be a url name?
#LOGIN_REDIRECT_URLNAME = "what_next"
LOGIN_REDIRECT_URLNAME = "home"
LOGOUT_REDIRECT_URLNAME = "home"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

'''
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]'''

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

# 将第三方app和主题加入到系统路径
sys.path.insert(0, THIRD_PARTY_ROOT)
sys.path.insert(0, THEME_ROOT)

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

INTERNAL_IPS = (
    "127.0.0.1",
    "192.168.195.1",
    # "192.168.128.122",
)

######################################  yt

TECHNOLOGY_REPORT_ROW = 13


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s]-[%(lineno)d]-%(levelname)s : %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s]-[%(lineno)d-%(funcName)s]-%(levelname)s : %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': os.path.join(PROJECT_ROOT, 'logs/all.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        'django': {
             'handlers': ['file', 'console'],
            'level':'INFO',
            'propagate': True,
        },
    },
}


# 启用批量检验, 功能完成后启用
IS_USE_BATCH_CHECK = True

# 使用的新的检验流程
USE_NEW_CHECK_FLOW = True

# 使用新的
USE_NEW_QA_MODAL = True

# 模板 URL ，对应路径为 os.path.join(PROJECT_ROOT, "static", "res")
TECHNOLOGY_TEMPLATE_LATEST_URL = STATIC_URL + 'res/technology_template_latest.xls'

