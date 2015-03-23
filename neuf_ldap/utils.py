# coding: utf-8
from __future__ import unicode_literals
from datetime import datetime
import pprint
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
        # Ignore
        pass


def ldap_user_group_exists(username):
    from neuf_ldap.models import LdapGroup

    return len(LdapGroup.objects.filter(name=username)) != 0


def ldap_username_exists(username):
    from neuf_ldap.models import LdapUser

    return len(LdapUser.objects.filter(username=username)) != 0


def create_ldap_user(user, dry_run=False):
    from neuf_ldap.models import LdapUser, LdapGroup

    def _get_next_uid():
        # Get user id order desc by id
        logger.debug('{} Getting next available UID'.format(datetime.utcnow()))
        users = LdapUser.objects.order_by('-id').values_list('id', flat=True)

        if len(users) == 0:
            return settings.LDAP_UID_MIN

        if users[0] >= settings.LDAP_UID_MAX:
            logger.exception("UID larger than LDAP_UID_MAX")

        return users[0] + 1

    def _get_next_user_gid():
        logger.debug('{} Getting next available GID for user group'.format(datetime.utcnow()))
        # Get user group ids order desc by id
        user_groups = LdapGroup.objects.order_by('-gid').values_list('gid', flat=True)

        if len(user_groups) == 0:
            return settings.LDAP_USER_GID_MIN

        if user_groups[0] >= settings.LDAP_USER_GID_MAX:
            logger.exception("UID larger than LDAP_USER_GID_MAX")

        return user_groups[0] + 1

    # User
    full_name = '{} {}'.format(user['first_name'], user['last_name'])
    user_data = {
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'full_name': full_name,
        'display_name': full_name,
        'gecos': user['username'],
        'email': user['email'],
        'username': user['username'],
        'id': _get_next_uid(),
        'group': _get_next_user_gid(),
        'home_directory': os.path.join(settings.LDAP_HOME_DIRECTORY_PREFIX, user['username'])
    }
    ldap_user = LdapUser(**user_data)

    # User password
    if user.get('password') is not None:
        ldap_user.set_password(user['password'], commit=False)  # Raw
        pwd_type = 'raw'
    elif user.get('ldap_password') is not None:
        ldap_user.password = user['ldap_password']  # Hashed
        pwd_type = 'hashed'
    else:
        # No password
        logger.error("User {} has no ldap_password (hashed) or password (unhashed), bailing!".format(user['username']))
        return False

    if not dry_run:
        ldap_user.save()
    logger.debug('User saved with data: {} and password type \'{}\'.'.format( pprint.pformat(user_data), pwd_type))

    # Add user group
    ldap_user_group = LdapGroup(name=user['username'], gid=user_data['group'], members=[user['username']])
    if not dry_run:
        ldap_user_group.save()
    logger.debug('User group {} created'.format(user['username']))

    # Add groups
    ldap_groups = LdapGroup.objects.filter(name__in=user['groups'])
    for g in ldap_groups:
        if user['username'] not in g.members:
            g.members.append(user['username'])
            if not dry_run:
                g.save()
            logger.debug('User {} added to group {}'.format(user['username'], g.name))

    # Finito!
    return True


def ldap_update_user_details(inside_user, dry_run=False):
    from neuf_ldap.models import LdapUser
    diff_attributes = ['username', 'email', 'groups']
    ldap_user = LdapUser.objects.get(username=inside_user['username'])

    for attr in diff_attributes:
        setattr(ldap_user, attr, inside_user[attr])

    if ldap_user.username != inside_user['username']:
        ldap_user.gecos = inside_user['username']

    name_changed = inside_user['first_name'] != ldap_user.first_name or inside_user['last_name'] != ldap_user.last_name
    if name_changed:
        full_name = '{} {}'.format(inside_user['first_name'], inside_user['last_name'])
        name_data = {
            'first_name': inside_user['first_name'],
            'last_name': inside_user['last_name'],
            'full_name': full_name,
            'display_name': full_name,
        }
        for key, value in name_data.iteritems():
            setattr(ldap_user, key, value)

    if not dry_run:
        ldap_user.save()
    logger.debug('User details updated for {}'.format(inside_user['username']))


def create_ldap_automount(username, dry_run=False):
    from neuf_ldap.models import LdapAutomountHome

    if len(LdapAutomountHome.objects.filter(username=username)) != 0:
        # Bail if it already exists
        return True

    automount = LdapAutomountHome(username=username)
    automount.set_automount_info()

    if not dry_run:
        automount.save()
    logger.debug('Automount {} added for user {}'.format(automount.automountInformation, username))

    return True
