# coding: utf-8
from __future__ import unicode_literals
import datetime
from django.conf import settings
import logging
import passwd
import re
from subprocess import Popen, PIPE

from models import Radcheck

logger = logging.getLogger(__name__)


def get_kerberos_principal(username):
    principal = "{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = " -p '{0}' -w {1} -q 'get_principal {2}'".format(
        settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
        settings.KERBEROS_PASSWORD,
        principal)
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_UNK_PRINC (principal does not exist)
        # KADM5_AUTH_GET (requires the get (inquire) privilege)
        logger.error(error)
        return None
    else:
        cleaned_output = {}
        match = re.findall(r'([\w ]*): (.+)', output)
        for key, value in match:
            cleaned_output[key] = value
        return cleaned_output


def set_kerberos_password(username, raw_password):
    principal = "{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = " -p {0} -w {1} -q 'change_password -pw {2} {3}'".format(
        settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
        settings.KERBEROS_PASSWORD,
        raw_password,
        principal)
    # FIXME: Running this shell command needs escaping: http://qntm.org/bash
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_AUTH_MODIFY (requires the modify privilege)
        logger.error(error)


def set_radius_password(username, raw_password):
    """
        Set password in Radius mysql backend. 
        Create user if one with an NT-Password does not exist.
    """
    pw_type = 'NT-Password'
    radius_defaults = {'attribute': pw_type, 'op': ':='}
    radius_user, created = Radcheck.objects.get_or_create(
        username=username,
        defaults=radius_defaults)

    # Some have clear text passwords!
    if radius_user.attribute != pw_type:
        radius_user.attribute = pw_type

    radius_user.value = passwd.radius_create(raw_password)
    radius_user.save()


def format_krb5_date(date):
    try:
        formatted_date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Z %Y')
        formatted_date = formatted_date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        formatted_date = 'never'
    return formatted_date
