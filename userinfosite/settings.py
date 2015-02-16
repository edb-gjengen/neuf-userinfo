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
        'USER': 'uid=test,ou=People,dc=neuf,dc=no',
        'PASSWORD': 'test',
    },
    'radius': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'radius',
        'USER': 'radius',
        'PASSWORD': '',
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
AUTH_LDAP_U_USER_SEARCH = LDAPSearch("ou=People,dc=neuf,dc=no", ldap.SCOPE_ONELEVEL, "(uid=%(user)s)")
# Basic groups
AUTH_LDAP_U_GROUP_SEARCH = LDAPSearch("ou=Groups,dc=neuf,dc=no", ldap.SCOPE_ONELEVEL, "(objectClass=posixGroup)")
AUTH_LDAP_U_GROUP_TYPE = PosixGroupType()
# Mirror groups on each auth
AUTH_LDAP_U_MIRROR_GROUPS = True
# Group to user flag mappings
AUTH_LDAP_U_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=dns-alle,ou=Groups,dc=neuf,dc=no",
    "is_staff": "cn=edb,ou=Groups,dc=neuf,dc=no",
    "is_superuser": "cn=edbadmin,ou=Groups,dc=neuf,dc=no"
}
# Group to profile flag mappings, not used.
AUTH_LDAP_U_PROFILE_FLAGS_BY_GROUP = {
    # "is_edb": "cn=edb,ou=Groups,dc=neuf,dc=no"
}
# User attribute mappings
AUTH_LDAP_U_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
# User profile attribute mappings
AUTH_LDAP_U_PROFILE_ATTR_MAP = {
    "home_directory": "homeDirectory"
}
# Allways update the django user object on authentication.
AUTH_LDAP_U_ALWAYS_UPDATE_USER = True

# Email LDAP auth
AUTH_LDAP_E_SERVER_URI = AUTH_LDAP_U_SERVER_URI
AUTH_LDAP_E_BIND_DN = AUTH_LDAP_U_BIND_DN
AUTH_LDAP_E_BIND_PASSWORD = AUTH_LDAP_U_BIND_PASSWORD

AUTH_LDAP_E_USER_SEARCH = LDAPSearch("ou=People,dc=neuf,dc=no", ldap.SCOPE_ONELEVEL, "(mail=%(user)s)")

AUTH_LDAP_E_GROUP_SEARCH = AUTH_LDAP_U_GROUP_SEARCH
AUTH_LDAP_E_GROUP_TYPE = AUTH_LDAP_U_GROUP_TYPE
AUTH_LDAP_E_MIRROR_GROUPS = AUTH_LDAP_U_MIRROR_GROUPS
AUTH_LDAP_E_USER_FLAGS_BY_GROUP = AUTH_LDAP_U_USER_FLAGS_BY_GROUP
AUTH_LDAP_E_PROFILE_FLAGS_BY_GROUP = AUTH_LDAP_U_PROFILE_FLAGS_BY_GROUP
AUTH_LDAP_E_USER_ATTR_MAP = AUTH_LDAP_U_USER_ATTR_MAP
AUTH_LDAP_E_PROFILE_ATTR_MAP = AUTH_LDAP_U_PROFILE_ATTR_MAP
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

try:
    from local_settings import *
except ImportError:
    pass