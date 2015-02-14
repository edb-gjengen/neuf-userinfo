# coding: utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, resolve_url, render
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
import json
from inside.models import InsideUser

from models import *
import utils


def index(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log the user in.
            login(request, form.get_user())
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('neuf_userinfo.views.profile'))
        else:
            form = AuthenticationForm(request)

    return render_to_response('public/index.html', locals(), context_instance=RequestContext(request))


@login_required
def profile(request):
    username = request.user.username
    groups = request.user.groups.all()
    ldap_user = None
    try:
        ldap_user = LdapUser.objects.get(username=username)
    except LdapUser.DoesNotExist:
        return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))

    ldap_groups = LdapGroup.objects.filter(usernames__contains=username)
    ldap_private_group = LdapGroup.objects.get(gid=ldap_user.group)

    return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))


@permission_required('main.is_superuser')
def user_profile(request, username):
    ldap_user = None
    try:
        ldap_user = LdapUser.objects.get(username=username)
    except LdapUser.DoesNotExist:
        return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))

    groups = LdapGroup.objects.filter(usernames__contains=username)
    private_group = LdapGroup.objects.get(gid=ldap_user.group)

    return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))


# TODO security
def client_status(request):
    krb5_principal = utils.get_kerberos_principal(request.GET.get('username'))
    if krb5_principal:
        last_succ_auth = utils.format_krb5_date(krb5_principal['Last successful authentication'])
        status = {
            'active': True,
            'last_successful_auth': last_succ_auth,
            'last_modified': krb5_principal['Last modified']
        }
    else:
        status = {'active': False}
    return HttpResponse(json.dumps(status), content_type='application/javascript; charset=utf8')


# TODO security
def wireless_status(request):
    username = request.GET.get('username')
    try:
        radius_user = Radcheck.objects.get(username=username)
    except Radcheck.ObjectDoesNotExist:
        return HttpResponse(json.dumps({'active': False}), content_type='application/javascript; charset=utf8')

    # get last authentication
    last_auth = Radpostauth.objects.filter(username__iexact=username, reply='Access-Accept').order_by('authdate')
    status = {'active': True, 'hash': radius_user.attribute}
    if len(last_auth) != 0:
        status['last_successful_auth'] = last_auth[0].authdate.strftime('%Y-%m-%d %H:%M:%S')

    return HttpResponse(json.dumps(status), content_type='application/javascript; charset=utf8')


def logout(request):
    auth_logout(request)
    return render(request, 'registration/logout.html')


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.

    Note: this is the same view as django.contrib.auth.views.password_reset_confirm
        with only minor changes for LDAP-lookup.
    """
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = InsideUser.objects.get(pk=uid)  # Diff line vs internal django view
    except (TypeError, ValueError, OverflowError, InsideUser.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
