from django.conf.urls.defaults import *
from django.contrib import admin
from main.forms import LDAPPasswordChangeForm
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^accounts/$', 'main.views.profile'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/password/change$', 'django.contrib.auth.views.password_change',
        {'password_change_form': LDAPPasswordChangeForm}),
    (r'^accounts/password/change/done$', 'django.contrib.auth.views.password_change_done'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/(?P<username>)/', 'main.views.profile'),
    (r'^$', 'main.views.index'),
)
