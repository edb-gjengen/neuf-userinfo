from django.conf.urls.defaults import *
from django.contrib import admin
from main.forms import LDAPPasswordChangeForm, LDAPSetPasswordForm, LDAPPasswordResetForm
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^accounts/$', 'main.views.profile'),
    # Change password
    (r'^accounts/password/change$', 'django.contrib.auth.views.password_change',
        {'password_change_form': LDAPPasswordChangeForm}),
    (r'^accounts/password/change/done$', 'django.contrib.auth.views.password_change_done'),
    # Reset password (forgot password)
    (r'^accounts/password/reset$', 'django.contrib.auth.views.password_reset',
        {'password_reset_form' : LDAPPasswordResetForm}),
    (r'^accounts/password/reset/done$', 'django.contrib.auth.views.password_reset_done'),
    # Set password
    (r'^accounts/password/reset/confirm$', 'main.views.password_reset_confirm',
        {'set_password_form': LDAPSetPasswordForm}),
    (r'^accounts/password/reset/complete$', 'django.contrib.auth.views.password_reset_complete'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/(?P<username>)/', 'main.views.profile'),
    (r'^$', 'main.views.index'),
)
