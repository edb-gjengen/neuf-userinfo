"""
Django settings for this project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a5p#+#0$i29xrc+z2!=s7nzp^m%5%v5^+^hfw7ouyah9#+1lpg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
)
INSTALLED_APPS += (
    'neuf_userinfo',
    'neuf_ldap',
    'neuf_radius',
    'neuf_kerberos',
    'inside',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'userinfosite.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
)

WSGI_APPLICATION = 'userinfosite.wsgi.application'

# LDAP (neuf.no)
LDAP_BASE_DN = "dc=neuf,dc=no"
LDAP_USER_DN = "ou=People,{}".format(LDAP_BASE_DN)
LDAP_GROUP_DN = "ou=Groups,{}".format(LDAP_BASE_DN)
LDAP_KERBEROS_DN = "cn=krbcontainer,{}".format(LDAP_BASE_DN)
LDAP_AUTOMOUNT_DN = "ou=Automount,{}".format(LDAP_BASE_DN)

LDAP_UID_MIN = 10000
LDAP_UID_MAX = 100000
LDAP_GID_MIN = 9000
LDAP_GID_MAX = 9999
LDAP_USER_GID_MIN = 10000
LDAP_USER_GID_MAX = 100000

LDAP_LOGIN_SHELL = '/bin/bash'
LDAP_HOME_DIRECTORY_PREFIX = '/home'
# Ref: http://tille.garrels.be/training/ldap/ch02s02.html
LDAP_SHADOW_LAST_CHANGE = 0  # Days since password last change
LDAP_SHADOW_MIN = 8  #
LDAP_SHADOW_MAX = 999999
LDAP_SHADOW_WARNING = 7  #
LDAP_SHADOW_EXPIRE = -1  #
LDAP_SHADOW_FLAG = 0

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://localhost/',
        'USER': 'uid=test,{}'.format(LDAP_USER_DN),
        'PASSWORD': 'test',
    },
    'radius': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_radius',
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': 'localhost',
    },
    'inside': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_inside',
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': 'localhost',
    }
}
DATABASE_ROUTERS = ['neuf_userinfo.router.Router']

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Oslo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Uploads
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_ID = 1

EMAIL_HOST = 'mx.neuf.no'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'noreply@neuf.no'

AUTHENTICATION_BACKENDS = (
    # 'inside.authentication.InsideBackend',
    'neuf_userinfo.backends.LDAPEmailBackend',
    'neuf_userinfo.backends.LDAPUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
)
# No cleaningladies.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 15  # in seconds

# LDAP server URI and BIND_DN, same as db-settings
AUTH_LDAP_U_SERVER_URI = DATABASES['ldap']['NAME']
AUTH_LDAP_U_BIND_DN = DATABASES['ldap']['USER']
AUTH_LDAP_U_BIND_PASSWORD = DATABASES['ldap']['PASSWORD']

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

# Basic user auth
AUTH_LDAP_U_USER_SEARCH = LDAPSearch(LDAP_USER_DN, ldap.SCOPE_ONELEVEL, "(uid=%(user)s)")
# Basic groups
AUTH_LDAP_U_GROUP_SEARCH = LDAPSearch(LDAP_GROUP_DN, ldap.SCOPE_ONELEVEL, "(objectClass=posixGroup)")
AUTH_LDAP_U_GROUP_TYPE = PosixGroupType()
# Mirror groups on each auth
AUTH_LDAP_U_MIRROR_GROUPS = True
# Group to user flag mappings
AUTH_LDAP_U_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=dns-alle,{}".format(LDAP_GROUP_DN),
    "is_staff": "cn=edb,{}".format(LDAP_GROUP_DN),
    "is_superuser": "cn=edbadmin,{}".format(LDAP_GROUP_DN)
}
# User attribute mappings
AUTH_LDAP_U_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
# Allways update the django user object on authentication.
AUTH_LDAP_U_ALWAYS_UPDATE_USER = True

# Email LDAP auth
AUTH_LDAP_E_SERVER_URI = AUTH_LDAP_U_SERVER_URI
AUTH_LDAP_E_BIND_DN = AUTH_LDAP_U_BIND_DN
AUTH_LDAP_E_BIND_PASSWORD = AUTH_LDAP_U_BIND_PASSWORD

AUTH_LDAP_E_USER_SEARCH = LDAPSearch(LDAP_USER_DN, ldap.SCOPE_ONELEVEL, "(mail=%(user)s)")

AUTH_LDAP_E_GROUP_SEARCH = AUTH_LDAP_U_GROUP_SEARCH
AUTH_LDAP_E_GROUP_TYPE = AUTH_LDAP_U_GROUP_TYPE
AUTH_LDAP_E_MIRROR_GROUPS = AUTH_LDAP_U_MIRROR_GROUPS
AUTH_LDAP_E_USER_FLAGS_BY_GROUP = AUTH_LDAP_U_USER_FLAGS_BY_GROUP
AUTH_LDAP_E_USER_ATTR_MAP = AUTH_LDAP_U_USER_ATTR_MAP
AUTH_LDAP_E_ALWAYS_UPDATE_USER = AUTH_LDAP_U_ALWAYS_UPDATE_USER

# Debug logging
import logging
logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Kerberos realm
KERBEROS_REALM = "NEUF.NO"
KERBEROS_PASSWORD_CHANGING_PRINCIPAL = 'brukerinfo'
KERBEROS_PASSWORD = ''

# Inside
INSIDE_GROUPS_SYNC_DELETE = True  # When user logs in, groups are synced (locally in Django), this deletes aswell
INSIDE_USERSYNC_API_KEY = ''
INSIDE_USERSYNC_ENC_KEY = ''

# Home dir
FILESERVER_HOST = "localhost"
FILESERVER_USER = 'nikolark'  # change this to your own user for development
FILESERVER_HOME_PATH = "/tmp/homes"

try:
    from local_settings import *
except ImportError:
    pass