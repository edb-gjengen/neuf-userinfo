from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

# My views
def index(request):
    return render_to_response('public/index.html', locals(), context_instance=RequestContext(request))

def profile(request, username):
    return render_to_response('private/profile.html', locals(), context_instance=RequestContext(request))


