from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin

from neuf_userinfo.forms import NeufPasswordChangeForm, NeufPasswordResetForm

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'', include('neuf_userinfo.urls')),
    url(r'', include('neuf_ldap.urls')),
    url(r'^userstatus/client/$', 'neuf_kerberos.views.client_status'),
    url(r'^userstatus/wireless/$', 'neuf_radius.views.wireless_status'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
)

# User account views
urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^accounts/login/$', 'login'),
    # Password
    url(r'^accounts/password/change$', 'password_change',
        {'password_change_form': NeufPasswordChangeForm}),
    url(r'^accounts/password/change/done$', 'password_change_done', name='password_change_done'),
    url(r'^accounts/password/reset$', 'password_reset',
        {'password_reset_form': NeufPasswordResetForm,
         'from_email': settings.DEFAULT_FROM_EMAIL,
         'email_template_name': 'registration/password_reset_email.txt',
         'html_email_template_name': 'registration/password_reset_email.html'}),
    url(r'^accounts/password/reset/done$', 'password_reset_done', name='password_reset_done'),
    url(r'^accounts/password/reset/complete$', 'password_reset_complete', name='password_reset_complete'),
)
