from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from neuf_radius.models import Radcheck, Radpostauth


@login_required
def wireless_status(request):
    username = request.GET.get('username')
    try:
        radius_user = Radcheck.objects.get(username=username)
    except Radcheck.DoesNotExist:
        return JsonResponse({'active': False})

    # get last authentication
    last_auth = Radpostauth.objects.filter(username__iexact=username, reply='Access-Accept').order_by('authdate')
    status = {'active': True, 'hash': radius_user.attribute}
    if len(last_auth) != 0:
        status['last_successful_auth'] = last_auth[0].authdate.strftime('%Y-%m-%d %H:%M:%S')

    return JsonResponse(status)