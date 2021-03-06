from __future__ import unicode_literals
import datetime
from django.conf import settings
import logging
import re
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

KADMIN_DATE_FORMAT = '%a %b %d %H:%M:%S %Z %Y'


def parse_kadmin_result(output):
    return dict(re.findall(r'([\w ]*): (.+)', output))


def get_kerberos_principal(username):
    principal = "{}@{}".format(username, settings.KERBEROS_REALM)
    kadmin_query = "get_principal {}".format(principal)
    output, error = _run_kadmin_query(kadmin_query)
    if error:
        # Can not init with KDC?
        # KADM5_UNK_PRINC (principal does not exist)
        # KADM5_AUTH_GET (requires the get (inquire) privilege)
        logger.warning(error)
        return None

    return parse_kadmin_result(output)


def has_kerberos_principal(username):
    return get_kerberos_principal(username) is not None


def set_kerberos_password(username, raw_password):
    principal = "{}@{}".format(username, settings.KERBEROS_REALM)
    kadmin_query = 'change_password -pw {} {}'.format(raw_password, principal)
    output, error = _run_kadmin_query(kadmin_query)
    if error:
        # Can not init with KDC?
        # KADM5_AUTH_MODIFY (requires the modify privilege)
        logger.warning(error)


def _run_kadmin_query(kadmin_query):
    kadmin_params = [
        '-p', settings.KERBEROS_ADMIN_PRINCIPAL,
        '-w', settings.KERBEROS_PASSWORD,
        '-q', kadmin_query]
    cmd = ['kadmin'] + kadmin_params
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)

    return p.communicate()


def format_krb5_date(date):
    try:
        formatted_date = datetime.datetime.strptime(date, KADMIN_DATE_FORMAT)
        formatted_date = formatted_date.isoformat()
    except ValueError:
        formatted_date = 'never'
    return formatted_date


def add_kerberos_principal(username, password, dry_run=False):
    principal = "{}@{}".format(username, settings.KERBEROS_REALM)
    kadmin_query = "add_principal -policy default -pw {} {}".format(
        password,
        principal)

    if not dry_run:
        output, error = _run_kadmin_query(kadmin_query)
        if error:
            # KADM5_AUTH_ADD (requires "add" privilege)
            # KADM5_BAD_MASK (shouldn't happen)
            # KADM5_DUP (principal exists already)
            # KADM5_UNK_POLICY (policy does not exist)
            # KADM5_PASS_Q_* (password quality violations)
            logger.error(error)
            return False

    logger.debug('Added kerberos principal {}'.format(principal))

    return True
