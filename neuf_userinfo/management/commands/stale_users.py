from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db.models import Q

from inside.models import InsideGroup, InsideUser
from neuf_ldap.models import LdapUser, LdapGroup

from optparse import make_option
# from neuf_userinfo.ssh import get_home_dirs


class Command(BaseCommand):
    help = 'List stale LDAP users not in the Inside group dns-aktiv'
    option_list = BaseCommand.option_list + (
        make_option(
            '--exclude-existing',
            action='store_true',
            dest='exclude_existing',
            default=False,
            help='Excludes users in the LDAP group dns-aktiv from the list'
        ),
    )

    ACTIVE_USERS_GROUP = 'dns-aktiv'
    options = {}

    def handle(self, *args, **options):
        self.options = options
        # home_dirs = get_home_dirs()
        inside_users_active = self.get_inside_users()
        ldap_users_all = self.get_ldap_users()
        stale_ldap_users = ldap_users_all - inside_users_active
        # stale_homedirs = set(home_dirs) - inside_users_active

        self.stdout.write('{} LDAP users not in group {} in Inside:\n{}'.format(
            len(stale_ldap_users),
            self.ACTIVE_USERS_GROUP,
            '\n'.join(stale_ldap_users)))
        self.stdout.write('')
        # self.stdout.write('{} stale home directories:\n{}'.format(
        #     len(stale_homedirs),
        #     '\n'.join(stale_homedirs)))

    def get_inside_users(self):
        group = InsideGroup.objects.get(posix_group=self.ACTIVE_USERS_GROUP)
        inside_users = InsideUser.objects.filter(group_rels__group=group)
        inside_users = inside_users.exclude(
            Q(ldap_username__isnull=True)
            | Q(registration_status='partial')
            | Q(ldap_password__isnull=True)).values_list('ldap_username', flat=True)

        if self.options['verbosity'] == '3':
            self.stdout.write('Found {} Inside users'.format(len(inside_users)))

        return set(inside_users)

    def get_ldap_users(self):
        # TODO: What about system users, should they be whitelisted?
        ldap_users = LdapUser.objects.all()
        if self.options['exclude_existing']:
            ldap_active_members = LdapGroup.objects.get(name=self.ACTIVE_USERS_GROUP).members
            ldap_users = ldap_users.exclude(username__in=ldap_active_members)
        ldap_users = ldap_users.values_list('username', flat=True)

        if self.options['verbosity'] == '3':
            self.stdout.write('Found {} LDAP users'.format(len(ldap_users)))

        return set(ldap_users)