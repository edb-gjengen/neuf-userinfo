from django.conf.urls import include, patterns, url
from django.contrib import admin
from neuf_userinfo.forms import NeufPasswordChangeForm, NeufSetPasswordForm, NeufPasswordResetForm
admin.autodiscover()

import settings

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^userstatus/client/$', 'neuf_userinfo.views.client_status'),
    url(r'^userstatus/wireless/$', 'neuf_userinfo.views.wireless_status'),
    url(r'^$', 'neuf_userinfo.views.index'),
)

# User account views
urlpatterns += patterns(
    '',
    url(r'^accounts/profile/$', 'neuf_userinfo.views.profile'),
    url(r'^accounts/profile/(?P<username>\w+)$', 'neuf_userinfo.views.user_profile'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'neuf_userinfo.views.logout'),

    # Change password
    url(r'^accounts/password/change$', 'django.contrib.auth.views.password_change',
        {'password_change_form': NeufPasswordChangeForm}),
    url(r'^accounts/password/change/done$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),

    # Reset password (forgot password)
    url(r'^accounts/password/reset$', 'django.contrib.auth.views.password_reset',
        {'password_reset_form': NeufPasswordResetForm, 'from_email': settings.DEFAULT_FROM_EMAIL}),
    url(r'^accounts/password/reset/done$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    # Set password
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'neuf_userinfo.views.password_reset_confirm',
        {'set_password_form': NeufSetPasswordForm}),
    url(r'^accounts/password/reset/complete$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
)