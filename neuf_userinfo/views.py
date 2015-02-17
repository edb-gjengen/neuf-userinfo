# coding: utf-8
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, resolve_url, render
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View

from inside.models import InsideUser
from neuf_ldap.models import LdapGroup, LdapUser
from neuf_userinfo.forms import NewUserForm
from neuf_userinfo.utils import decrypt_rijndael


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
    # FIXME: Allmost identical to below
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
        user = InsideUser.objects.get(pk=uid)  # Diff vs internal Django view
    except (TypeError, ValueError, OverflowError, InsideUser.DoesNotExist):  # Diff vs internal Django view
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

    return TemplateResponse(request, template_name, context, current_app=current_app)


class AddNewUserView(View):

    def get(self, request):
        """
            - Create new user in LDAP (username, first_name, last_name, email)
            - add to groups (usergroup, dns-alle), it not exists, create
            - Set LDAP password
            - Create automount entry
            - Create kerberos principal and set password
            - Create homedir on wii
            - Set RADIUS password
        """

        if not self.validate_api_key(request.GET.get('api_key', '')):
            return JsonResponse({'errors': 'Invalid api_key'})

        form = NewUserForm(request.GET)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors})

        user = form.cleaned_data
        # print "yey", user
        # TODO you are still here

        result = {'yousir': 'are a scholar!'}
        return JsonResponse(result)

    def validate_api_key(self, api_key):
        if api_key == '' or api_key != settings.INSIDE_USERSYNC_API_KEY:
            return False

        return True