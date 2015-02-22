from neuf_radius.models import Radcheck, Radpostauth
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'OPTIONS', 'HEAD'])
def wireless_status(request):
    username = request.QUERY_PARAMS.get('username')
    try:
        radius_user = Radcheck.objects.get(username=username)
    except Radcheck.DoesNotExist:
        return Response({'active': False})

    # get last authentication
    last_auth = Radpostauth.objects.filter(username__iexact=username, reply='Access-Accept').order_by('authdate')
    status = {'active': True, 'hash': radius_user.attribute}
    if len(last_auth) != 0:
        status['last_successful_auth'] = last_auth[0].authdate.strftime('%Y-%m-%d %H:%M:%S')

    return Response(status)