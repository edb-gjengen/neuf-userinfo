from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import base36_to_int
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.contrib.auth.tokens import default_token_generator


from forms import LDAPPasswordResetForm
from models import *

# My views
def index(request):
    return render_to_response('public/index.html', locals(), context_instance=RequestContext(request))

@login_required
def profile(request, username=None):
    ldap_user = ""
    try:
        ldap_user = LdapUser.objects.get(username=request.user)
    except:
        pass

    return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))

# Doesn't need csrf_protect since no-one can guess the URL
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.

    Note: this is the same view as django.contrib.auth.views.password_reset_confirm
        with only minor changes.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = LdapUser.objects.get(uid=uid_int) # Diff line vs internal django view 
    except (ValueError, User.DoesNotExist):
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
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))

