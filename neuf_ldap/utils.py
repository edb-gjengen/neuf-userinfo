# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings
import logging
import os
from passlib.hash import ldap_salted_sha1

logger = logging.getLogger(__name__)


def ldap_create(raw_password):
    return ldap_salted_sha1.encrypt(raw_password)


def ldap_validate(raw_password, challenge_password):
    # challenge_password is hash from db
    # raw_password is the cleartext password.
    return ldap_salted_sha1.validate(raw_password, challenge_password)


def set_ldap_password(username, raw_password):
    from neuf_ldap.models import LdapUser
    try:
        # LDAP: Lookup the Ldap user with the identical username (1-to-1).
        user = LdapUser.objects.get(username=username)
        user.set_password(raw_password)
    except LdapUser.DoesNotExist:
        pass


def ldap_user_group_exists(username):
    from neuf_ldap.models import LdapGroup

    return len(LdapGroup.objects.filter(name=username)) != 0


def ldap_username_exists(username):
    from neuf_ldap.models import LdapUser

    return len(LdapUser.objects.filter(username=username)) != 0


def ldap_create_user(user):
    from neuf_ldap.models import LdapUser, LdapGroup

    def _get_next_uid():
        # Get user ids between min and max, and order desc by id
        users = LdapUser.objects.filter(id__gte=settings.LDAP_UID_MIN, id__lte=settings.LDAP_UID_MAX)
        users = users.order_by('-id').values_list('id', flat=True)

        if len(users) == 0:
            return settings.LDAP_UID_MIN

        if len(users) > 0 and users[0] >= settings.LDAP_UID_MAX:
            logger.exception("UID larger than LDAP_UID_MAX")

        return users[0] + 1

    def _get_next_user_gid():
        # Get user group ids between min and max, and order desc by id
        user_groups = LdapGroup.objects.filter(gid__gte=settings.LDAP_USER_GID_MIN, gid__lte=settings.LDAP_USER_GID_MAX)
        user_groups = user_groups.order_by('-gid').values_list('gid', flat=True)

        if len(user_groups) == 0:
            return settings.LDAP_USER_GID_MIN

        if len(user_groups) > 0 and user_groups[0] >= settings.LDAP_USER_GID_MAX:
            logger.exception("UID larger than LDAP_USER_GID_MAX")

        return user_groups[0] + 1

    # User
    full_name = '{} {}'.format(user['firstname'], user['lastname'])
    user_data = {
        'first_name': user['firstname'],
        'last_name': user['lastname'],
        'full_name': full_name,
        'display_name': full_name,
        'gecos': full_name,
        'email': user['email'],
        'username': user['username'],
        'id': _get_next_uid(),
        'group': _get_next_user_gid(),
        'home_directory': os.path.join(settings.LDAP_HOME_DIRECTORY_PREFIX, user['username'])
    }
    ldap_user = LdapUser(**user_data)
    ldap_user.set_password(user['password'], commit=False)
    ldap_user.save()

    # Add user group
    ldap_user_group = LdapGroup(name=user['username'], gid=user_data['group'], members=[user['username']])
    ldap_user_group.save()

    # Add groups
    ldap_groups = LdapGroup.objects.filter(name__in=user['groups'])
    for g in ldap_groups:
        if user['username'] not in g.members:
            g.members.append(user['username'])
            g.save()

    # Finito!
    return True


def ldap_create_automount(username):
    from neuf_ldap.models import LdapAutomountHome
    automount = LdapAutomountHome(username=username)
    automount.set_automount_info()
    automount.save()

    return True
