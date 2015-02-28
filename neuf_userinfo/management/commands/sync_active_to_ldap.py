from django.conf import settings
from django.core.management.base import BaseCommand

from inside.models import InsideGroup, InsideUser
from neuf_ldap.models import LdapGroup, LdapUser
from neuf_ldap.utils import ldap_create_user


class Command(BaseCommand):
    help = 'Syncs users in group dns-aktiv from Inside to LDAP'
    DIFF_ATTRIBUTES = ['username', 'first_name', 'last_name', 'email', 'groups']
    COUNTS = dict(create=0, update=0, in_sync=0)

    def handle(self, *args, **options):
        # Get all active user from Inside
        inside_users_diffable = self.get_inside_users_diffable()
        if options['verbosity'] == '3':
            self.stdout.write('Found {} Inside users'.format(len(inside_users_diffable)))

        # Get existing users in LDAP
        ldap_users_diffable = self.get_ldap_users_diffable()
        if options['verbosity'] == '3':
            self.stdout.write('Found {} LDAP users'.format(len(ldap_users_diffable)))

        self.sync_users(inside_users_diffable, ldap_users_diffable, options)

        self.obsolete_users(inside_users_diffable, ldap_users_diffable, options)

        self.log_totals(options)
        # Voila

    def sync_users(self, inside_users_diffable, ldap_users_diffable, options):
        for username, u in inside_users_diffable.iteritems():
            # Diff by username
            if username not in ldap_users_diffable:
                # TODO create
                # ldap_create_user(u)
                self.COUNTS['create'] += 1
                if int(options['verbosity']) >= 2:
                    self.stdout.write('Inside user {} is not in LDAP'.format(username))
            elif not self.user_details_in_sync(u, ldap_users_diffable[username]):
                # TODO update
                # ldap_update_user(u)
                self.COUNTS['update'] += 1
                if int(options['verbosity']) >= 2:
                    self.stdout.write('Inside user {} is out of sync with LDAP'.format(username))
            else:
                self.COUNTS['in_sync'] += 1
                if int(options['verbosity']) == 3:
                    self.stdout.write('Inside user {} is in sync with LDAP'.format(username))

    def obsolete_users(self, inside_users_diffable, ldap_users_diffable, options):
        for username, u in ldap_users_diffable.iteritems():
            if username not in inside_users_diffable:
                if int(options['verbosity']) >= 2:
                    self.stdout.write('LDAP user {} is not in Inside'.format(username))

    def log_totals(self, options):
        if self.COUNTS['create'] != 0:
            self.stdout.write('{} Inside users not found in LDAP'.format(self.COUNTS['create']))
        if self.COUNTS['update'] != 0:
            self.stdout.write('{} LDAP users were were update with info '.format(self.COUNTS['update']))
        if int(options['verbosity']) >= 2:
            self.stdout.write('{} Inside users in sync with LDAP users '.format(self.COUNTS['in_sync']))

    def get_inside_users_diffable(self):
        inside_users_diffable = {}
        group = InsideGroup.objects.get(posix_group='dns-aktiv')
        inside_users = InsideUser.objects.filter(group_rels__group=group)

        for u in inside_users:
            inside_groups = InsideGroup.objects.filter(user_rels__user=u).exclude(posix_group='')
            inside_groups = inside_groups.values_list('posix_group', flat=True)
            inside_users_diffable[u.ldap_username] = {
                'username': u.ldap_username,
                'first_name': u.firstname,
                'last_name': u.lastname,
                'password': u.ldap_password,
                'email': u.email,
                'groups': inside_groups
            }
        return inside_users_diffable

    def get_ldap_users_diffable(self):
        ldap_users_diffable = {}
        ldap_active_members = LdapGroup.objects.get(name="dns-aktiv").members
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
        return ldap_users_diffable

    def user_details_in_sync(self, inside_user, ldap_user):
        for attr in self.DIFF_ATTRIBUTES:
            if inside_user[attr] != ldap_user[attr]:
                # Groups are lists
                if type(attr) != list:
                    return False
                elif set(inside_user[attr]) != set(ldap_user[attr]):
                    return False

        return True