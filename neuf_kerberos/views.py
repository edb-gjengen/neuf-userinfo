from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from neuf_kerberos.utils import get_kerberos_principal, format_krb5_date


@login_required
def client_status(request):
    krb5_principal = get_kerberos_principal(request.GET.get('username'))
    if not krb5_principal:
        return JsonResponse({'active': False})

    last_succ_auth = format_krb5_date(krb5_principal['Last successful authentication'])
    status = {
        'active': True,
        'last_successful_auth': last_succ_auth,
        'last_modified': krb5_principal['Last modified']
    }

    return JsonResponse(status)