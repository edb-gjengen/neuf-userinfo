from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from inside.models import InsideGroup, InsideUser
from neuf_ldap.models import LdapGroup, LdapUser
from neuf_ldap.utils import ldap_create_user, ldap_update_user_details

from optparse import make_option
from neuf_userinfo.utils import add_new_user

ACTIVE_USERS_GROUP = 'dns-aktiv'


class Command(BaseCommand):
    help = 'Syncs users in group dns-aktiv from Inside to LDAP'
    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run of syncronization, nothing is saved.'
        ),)

    DIFF_ATTRIBUTES = ['username', 'first_name', 'last_name', 'email', 'groups']
    COUNTS = dict(create=0, update=0, in_sync=0)
    options = {}

    def handle(self, *args, **options):
        self.options = options

        # Get all active user from Inside
        inside_users_diffable = self.get_inside_users_diffable()

        # Get existing users in LDAP
        ldap_users_diffable = self.get_ldap_users_diffable()

        # Do actual sync
        self.sync_users(inside_users_diffable, ldap_users_diffable)

        # Are any LDAP users stale?
        self.stale_ldap_users(inside_users_diffable, ldap_users_diffable)

        self.log_totals()

        # Voila!

    def get_inside_users_diffable(self):
        inside_users_diffable = {}
        group = InsideGroup.objects.get(posix_group=ACTIVE_USERS_GROUP)
        inside_users = InsideUser.objects.filter(group_rels__group=group)
        inside_users = inside_users.exclude(Q(ldap_username__isnull=True) | Q(registration_status='partial'))

        for u in inside_users:
            inside_groups = InsideGroup.objects.filter(user_rels__user=u).exclude(posix_group='')
            inside_groups = inside_groups.values_list('posix_group', flat=True)
            inside_users_diffable[u.ldap_username] = {
                'username': u.ldap_username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'ldap_password': u.ldap_password,
                'email': u.email,
                'groups': inside_groups
            }
        if self.options['verbosity'] == '3':
            self.stdout.write('Found {} Inside users'.format(len(inside_users_diffable)))

        return inside_users_diffable

    def get_ldap_users_diffable(self):
        ldap_users_diffable = {}
        ldap_active_members = LdapGroup.objects.get(name=ACTIVE_USERS_GROUP).members
        ldap_users = LdapUser.objects.filter(username__in=ldap_active_members)

        for u in ldap_users:
            ldap_groups = LdapGroup.objects.filter(members__contains=u.username).values_list('name', flat=True)
            ldap_users_diffable[u.username] = {
                'username': u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'groups': ldap_groups
            }
        if self.options['verbosity'] == '3':
            self.stdout.write('Found {} LDAP users'.format(len(ldap_users_diffable)))

        return ldap_users_diffable

    def sync_users(self, inside_users_diffable, ldap_users_diffable):
        for username, user in inside_users_diffable.iteritems():
            if username not in ldap_users_diffable:
                # Create
                add_new_user(user, dry_run=self.options['dry_run'])

                self.COUNTS['create'] += 1
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('Inside user {} is not in LDAP'.format(username))
            elif not self.user_details_in_sync(user, ldap_users_diffable[username]):
                # Update
                ldap_update_user_details(user, dry_run=self.options['dry_run'])

                self.COUNTS['update'] += 1
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('Inside user {} is out of sync with LDAP'.format(username))
            else:
                # In sync :-)
                self.COUNTS['in_sync'] += 1
                if int(self.options['verbosity']) == 3:
                    self.stdout.write('Inside user {} is in sync with LDAP'.format(username))

    def stale_ldap_users(self, inside_users_diffable, ldap_users_diffable):
        for username, u in ldap_users_diffable.iteritems():
            if username not in inside_users_diffable:
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('LDAP user {} is not in Inside'.format(username))

    def log_totals(self):
        if self.COUNTS['create'] != 0:
            self.stdout.write('{} Inside users not found in LDAP'.format(self.COUNTS['create']))
        if self.COUNTS['update'] != 0:
            self.stdout.write('{} LDAP users were were update with info '.format(self.COUNTS['update']))
        if int(self.options['verbosity']) >= 2:
            self.stdout.write('{} Inside users in sync with LDAP users '.format(self.COUNTS['in_sync']))

    def user_details_in_sync(self, inside_user, ldap_user):
        for attr in self.DIFF_ATTRIBUTES:
            if inside_user[attr] != ldap_user[attr]:
                # Groups are lists
                if type(attr) != list:
                    return False
                elif set(inside_user[attr]) != set(ldap_user[attr]):
                    return False

        return True