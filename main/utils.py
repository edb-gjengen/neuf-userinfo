# coding: utf-8
import re

from subprocess import Popen, PIPE
from django.core.exceptions import ObjectDoesNotExist

from models import Radcheck
import passwd
import settings

def get_kerberos_principal(username):
    principal = u"{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = u"-p {0} -w {1} -q 'get_principal {2}'".format(settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
                                                                settings.KERBEROS_PASSWORD,
                                                                principal)
    p = Popen(['kadmin', kadmin_query], stdout=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_UNK_PRINC (principal does not exist)
        # KADM5_AUTH_GET (requires the get (inquire) privilege)
        return None
    else:
        cleaned_output = {}
        match = re.findall(r'([\w ]*): (.+)', output)
        for key,value in match:
            cleaned_output[key] = value
        return cleaned_output

def set_kerberos_password(username, raw_password):
    principal = u"{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = u"-p {0} -w {1} -q 'change_password {2} -pw {3}'".format(settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
                                                                          settings.KERBEROS_PASSWORD,
                                                                          principal,
                                                                          raw_password)
    p = Popen(['kadmin', kadmin_query], stdout=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_AUTH_MODIFY (requires the modify privilege)
        return False
    else:
        return True

def set_radius_password(username, raw_password):
    try:
        radius_user = Radcheck.objects.get(username=username)
    except ObjectDoesNotExist:
        return False
    radius_user.value = passwd.radius_create(raw_password)
    radius_user.save()
    return True
