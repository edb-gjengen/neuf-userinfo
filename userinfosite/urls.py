from django.conf.urls import include, patterns, url
from django.contrib import admin
from main.forms import LDAPPasswordChangeForm, LDAPSetPasswordForm, LDAPPasswordResetForm
admin.autodiscover()

import settings

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/profile/$', 'main.views.profile'),
    url(r'^accounts/profile/(?P<username>\w+)$', 'main.views.user_profile'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'main.views.logout'),
    # Change password
    url(r'^accounts/password/change$', 'django.contrib.auth.views.password_change',
        {'password_change_form': LDAPPasswordChangeForm}),
    url(r'^accounts/password/change/done$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    # Reset password (forgot password)
    url(r'^accounts/password/reset$', 'django.contrib.auth.views.password_reset',
        {'password_reset_form' : LDAPPasswordResetForm,
         'from_email' : settings.FROM_EMAIL}),
    url(r'^accounts/password/reset/done$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    # Set password
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$',
        'main.views.password_reset_confirm',
        {'set_password_form': LDAPSetPasswordForm}),
    url(r'^accounts/password/reset/complete$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^userstatus/client/$', 'main.views.client_status'),
    url(r'^userstatus/wireless/$', 'main.views.wireless_status'),
    url(r'^$', 'main.views.index'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns # for dev
urlpatterns += staticfiles_urlpatterns()
