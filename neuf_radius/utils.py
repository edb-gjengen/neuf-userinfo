# coding: utf-8
from __future__ import unicode_literals
import logging
from passlib.hash import nthash

from neuf_radius.models import Radcheck

logger = logging.getLogger(__name__)


def radius_create(raw_password):
    return nthash.encrypt(raw_password)


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

    radius_user.value = radius_create(raw_password)
    radius_user.save()


def radius_create_user(username, password, dry_run=False):
    if not dry_run:
        set_radius_password(username, password)
    else:
        logger.debug('Setting radius password for \'{}\''.format(username))

    return True