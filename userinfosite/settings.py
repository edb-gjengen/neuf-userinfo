"""
Ref: https://docs.djangoproject.com/en/1.8/ref/settings/
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
    'flat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
)
INSTALLED_APPS += (
    'rest_framework',
    'neuf_userinfo',
    'neuf_ldap',
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
        'USER': 'cn=admin,dc=neuf,dc=no',
        'PASSWORD': 'toor',
    },
    'inside': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'inside-db.sqlite3'),
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
    'inside.authentication.InsideBackend',
    'django.contrib.auth.backends.ModelBackend',
)
# No cleaningladies.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 15  # in seconds

# Kerberos realm
KERBEROS_REALM = "NEUF.NO"
KERBEROS_ADMIN_PRINCIPAL = 'brukerinfo'
KERBEROS_PASSWORD = ''

# Inside
INSIDE_AUTH_USER_FLAGS_SYNC = {
    "is_active": "dns-alle",
    # "is_staff": "edb",
    # "is_superuser": "edbadmin"
}
INSIDE_AUTH_GROUPS_SYNC_DELETE = True  # When user logs in, groups are synced (locally in Django), this deletes aswell

INSIDE_USERSYNC_API_KEY = ''
INSIDE_USERSYNC_ENC_KEY = ''
INSIDE_USERSYNC_RUN_SYNCHRONOUS = False

# Home dir
FILESERVER_HOST = "localhost"
FILESERVER_SSH_USER = 'nikolark'  # change this to your own user for development
FILESERVER_SSH_KEY_PATH = ''  # e.g. '/home/nikolark/.ssh/id_rsa'
FILESERVER_HOME_PATH = "/tmp/"
FILESERVER_CREATE_HOMEDIR_SCRIPT = os.path.join(BASE_DIR, 'scripts', 'create_home_directory.sh')

# Wordpress sync
WP_PHP_SCRIPT_PATH = os.path.join(BASE_DIR, 'scripts')
WP_OUT_FILENAME = os.path.join(WP_PHP_SCRIPT_PATH, "users_in_group_active.json")
WP_LOAD_PATHS = [
    "/var/www/studentersamfundet.no/www/wp/wp-load.php",
    "/var/www/neuf.no/aktivweb/wp-load.php"
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': 10
}

# CELERY SETTINGS
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


try:
    from .local_settings import *
except ImportError:
    pass
