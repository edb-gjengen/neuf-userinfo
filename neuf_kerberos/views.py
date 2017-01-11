from rest_framework.decorators import api_view
from rest_framework.response import Response

from neuf_kerberos.utils import get_kerberos_principal, format_krb5_date


@api_view(['GET', 'OPTIONS', 'HEAD'])
def client_status(request):
    krb5_principal = get_kerberos_principal(request.GET.get('username'))
    if not krb5_principal:
        return Response({'active': False})

    last_succ_auth = format_krb5_date(krb5_principal['Last successful authentication'])
    status = {
        'active': True,
        'last_successful_auth': last_succ_auth,
        'last_modified': krb5_principal['Last modified']
    }

    return Response(status)