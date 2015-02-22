import datetime
from django.conf import settings
import logging
import re
from subprocess import Popen, PIPE

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

    cleaned_output = {}
    match = re.findall(r'([\w ]*): (.+)', output)
    for key, value in match:
        cleaned_output[key] = value

    return cleaned_output


def set_kerberos_password(username, raw_password):
    principal = "{}@{}".format(username, settings.KERBEROS_REALM)
    kadmin_query = " -p {} -w {} -q 'change_password -pw {} {}'".format(
        settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
        settings.KERBEROS_PASSWORD,
        raw_password,
        principal)
    # FIXME: Running this shell command could need escaping: http://qntm.org/bash
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_AUTH_MODIFY (requires the modify privilege)
        logger.error(error)


def format_krb5_date(date):
    try:
        formatted_date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Z %Y')
        formatted_date = formatted_date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        formatted_date = 'never'
    return formatted_date


def kerberos_create_principal(username, password):
    principal = "{}@{}".format(username, settings.KERBEROS_REALM)
    kadmin_query = " -p '{}' -w {} -q 'add_principal {} -pw {}'".format(
        settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
        settings.KERBEROS_PASSWORD,
        principal,
        password)
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if error:
        # KADM5_AUTH_ADD (requires "add" privilege)
        # KADM5_BAD_MASK (shouldn't happen)
        # KADM5_DUP (principal exists already)
        # KADM5_UNK_POLICY (policy does not exist)
        # KADM5_PASS_Q_* (password quality violations)
        logger.error(error)
        return False

    return True