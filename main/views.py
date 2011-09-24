from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from models import *

# My views
@login_required
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
