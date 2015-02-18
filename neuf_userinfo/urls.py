from django.conf.urls import patterns, url
from neuf_userinfo.forms import NeufSetPasswordForm
from neuf_userinfo.views import AddNewUserView

urlpatterns = patterns(
    'neuf_userinfo.views',
    url(r'^$', 'index', name='index'),
    url(r'^accounts/profile/(?P<username>\w*)$', 'profile'),
    url(r'^accounts/logout/$', 'logout'),
    # Set password
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',
        {'set_password_form': NeufSetPasswordForm}),
)

# Rewrite of usersync.neuf.no
urlpatterns += patterns(
    '',
    url(r'^usersync/$', AddNewUserView.as_view(), name='usersync'),
)