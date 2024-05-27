from .common import *
from .logging_local import LOGGING
from configparser import ConfigParser

WSGI_APPLICATION = 'config.wsgi.application'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

config = ConfigParser()
filename = os.path.join(os.path.split(__file__)[0], 'trading.conf')
print(filename)
config.read(filename)

sysname  = config.get('default', 'sysname')
if not sysname:
    raise ValueError

dbname = config.get(sysname, 'dbname')
dbhost = config.get(sysname, 'dbhost')
user = config.get(sysname, 'user')
password = config.get(sysname, 'password')
IMAGES_PATH = config.get(sysname, 'images_path')
sentryhost = config.get(sysname, 'sentryhost')


