from .common import *
from .logging import LOGGING
from configparser import ConfigParser

WSGI_APPLICATION = 'config.wsgi.application'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

config = ConfigParser()
filename = os.path.join(os.path.split(__file__)[0], 'trading.conf')
print(filename)
config.read(filename)

sysname  = config.get('default', 'sysname')
if not sysname:
    raise ValueError
use_db = config.get(sysname, 'use_db', fallback=False)
dbname = config.get(sysname, 'dbname')
dbhost = config.get(sysname, 'dbhost')
user = config.get(sysname, 'user')
password = config.get(sysname, 'password')
IMAGES_PATH = config.get(sysname, 'images_path')
sentryhost = config.get(sysname, 'sentryhost')
serverIP   = config.get(sysname, 'serverIP', fallback=None)
if serverIP:
    ALLOWED_HOSTS += [serverIP]

# email
EMAIL_HOST_USER = config.get('default', 'email_host_user')
EMAIL_HOST_PASSWORD = config.get('default', 'email_host_password')


if use_db == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, dbname),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': dbname,
            'USER': user,
            'PASSWORD': password,
            'HOST': dbhost,
            'PORT': 3306,
            # 'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO'",
                'charset': 'utf8mb4',
                'use_unicode': True,
            }
        }
    }

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=sentryhost,
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.5,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

if DEBUG:
   print('debug tool enabled')
   INTERNAL_IPS = ('127.0.0.1', 'localhost')
   MIDDLEWARE += (
       'debug_toolbar.middleware.DebugToolbarMiddleware',
   )

   INSTALLED_APPS += (
       'debug_toolbar',
   )

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
       'debug_toolbar.panels.profiling.ProfilingPanel',
   ]

   DEBUG_TOOLBAR_CONFIG = {
       'INTERCEPT_REDIRECTS': False,
   }
