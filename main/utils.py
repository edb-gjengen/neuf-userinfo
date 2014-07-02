# coding: utf-8
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from subprocess import Popen, PIPE
import datetime
import re

from models import Radcheck
import passwd

def get_kerberos_principal(username):
    principal = u"{0}@{1}".format(username, settings.KERBEROS_REALM)
    kadmin_query = u" -p '{0}' -w {1} -q 'get_principal {2}'".format(settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
            settings.KERBEROS_PASSWORD,
            principal)
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
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
    kadmin_query = u" -p {0} -w {1} -q 'change_password -pw {2} {3}'".format(settings.KERBEROS_PASSWORD_CHANGING_PRINCIPAL,
            settings.KERBEROS_PASSWORD,
            raw_password,
            principal)
    # Note: Running this shell command could need escaping: http://qntm.org/bash
    p = Popen('kadmin' + kadmin_query, shell=True, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if error:
        # Can not init with KDC?
        # KADM5_AUTH_MODIFY (requires the modify privilege)
        return False
    else:
        return True

def set_radius_password(username, raw_password):
    """
        Set password in Radius mysql backend. 
        Create user if one with an NT-Password does not exist.
    """
    try:
        radius_user = Radcheck.objects.get(username=username)
    except ObjectDoesNotExist:
        radius_user = Radcheck(username=username, attribute='NT-Password', op=':=')
    
    # Some have clear text passwords!
    if radius_user.attribute != 'NT-Password':
        radius_user.attribute = 'NT-Password'

    radius_user.value = passwd.radius_create(raw_password)
    radius_user.save()
    return True

def log_inside_userupdate(username, message):
    from django.db import connections
    c = connections['inside'].cursor()

    # TODO errorhandling
    try:
        c.execute("SELECT id FROM din_user WHERE username= %s", [username])
        row = c.fetchone()
        if row is not None:
            user_id = row[0]
            c.execute(
                "INSERT INTO din_userupdate (date, user_id_updated, comment, user_id_updated_by) VALUES (NOW(), %s, %s, %s)",
                [user_id, message, user_id])
    finally:
        c.close()

    return True

def set_inside_password(username, raw_password):
    from django.db import connections
    c = connections['inside'].cursor()

    # TODO errorhandling
    try:
        c.execute("UPDATE din_user SET password=PASSWORD(%s) WHERE username=%s", [raw_password, username])
    finally:
        c.close()

    log_inside_userupdate(username, u"Satt passord på nytt via brukerinfo.neuf.no.")

    return True

def format_krb5_date(date):
    try:
        formatted_date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Z %Y')
        formatted_date = formatted_date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        formatted_date = 'never'
    return formatted_date
