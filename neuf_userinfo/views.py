# coding: utf-8
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponseNotFound
from django.shortcuts import resolve_url, render, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View
import logging

from inside.models import InsideUser
from neuf_userinfo.forms import NewUserForm
from neuf_userinfo.tasks import add_new_user
from neuf_userinfo.utils import add_new_user_sync

logger = logging.getLogger(__name__)


def index(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log the user in.
            login(request, form.get_user())
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('my-profile'))
        else:
            form = AuthenticationForm(request)

    return render(request, 'public/index.html', {'form': form})


@login_required
def profile(request, username=''):
    if username != '' and not request.user.is_superuser:
        # Only allow superusers
        return HttpResponseNotFound()

    if username != '':
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    response = {
        'groups': user.groups.all(),
        'user': user
    }
    return render(request, 'private/profile.html', response)


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
        """ Adds a new user to all our internal services. See .utils.add_new_user for details. """

        if not self.validate_api_key(request.GET.get('api_key', '')):
            return JsonResponse({'errors': 'Invalid api_key'})

        form = NewUserForm(request.GET)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors})

        user = form.cleaned_data
        logger.debug('Adding user \'{}\'.'.format(user['username']))

        if settings.INSIDE_USERSYNC_RUN_SYNC:
            add_new_user_sync(user)
        else:
            add_new_user.delay(user)  # Async

        return JsonResponse({'results': 'success'})

    def validate_api_key(self, api_key):
        if api_key == '' or api_key != settings.INSIDE_USERSYNC_API_KEY:
            return False

        return True