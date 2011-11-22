# coding: utf-8
from subprocess import Popen, PIPE
from django.core.exceptions import ObjectDoesNotExist

from models import Radcheck
import passwd
import settings

def set_kerberos_password(username, raw_password):
    principal = u"{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = u"-q change_password {0} -pw {1}".format(principal, raw_password)
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
