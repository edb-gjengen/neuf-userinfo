from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q

from inside.models import InsideGroup, InsideUser
from neuf_ldap.models import LdapGroup, LdapUser
from neuf_ldap.utils import create_ldap_user, ldap_update_user_details, create_ldap_automount, ldap_update_user_groups

from optparse import make_option
from neuf_userinfo.ssh import create_home_dir

ACTIVE_USERS_GROUP = 'dns-aktiv'


class Command(BaseCommand):
    help = 'Synchronizes users in group dns-aktiv from Inside to LDAP'
    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run when syncronizing, does not save anything.'
        ),
        make_option(
            '--delete-group-memberships',
            action='store_true',
            dest='delete_group_memberships',
            default=False,
            help='Toggle if group memberships syncronization should delete or not'
        ),)

    DIFF_ATTRIBUTES = ['first_name', 'last_name', 'email']
    SYNC_GROUP_PREFIX = 'dns-'
    COUNTS = dict(create=0, update=0, in_sync=0)
    options = {}

    def handle(self, *args, **options):
        self.options = options
        if int(self.options['verbosity']) >= 2:
            self.stdout.write('[{}] Started sync job'.format(datetime.utcnow()))

        # Get all active user from Inside
        inside_users_diffable = self.get_inside_users_diffable()

        # Get existing users in LDAP
        ldap_users_diffable = self.get_ldap_users_diffable()

        # Do actual sync
        self.sync_users(inside_users_diffable, ldap_users_diffable)

        self.log_totals()

        if int(self.options['verbosity']) >= 2:
            self.stdout.write('[{}] Finished sync job'.format(datetime.utcnow()))

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
            ldap_groups = LdapGroup.objects\
                .filter(name__startswith=self.SYNC_GROUP_PREFIX, members__contains=u.username)\
                .values_list('name', flat=True)
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
                create_ldap_user(user, dry_run=self.options['dry_run'])
                create_home_dir(user['username'], dry_run=self.options['dry_run'])
                create_ldap_automount(user['username'], dry_run=self.options['dry_run'])

                self.COUNTS['create'] += 1
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('[CREATED] Inside user {} is not in LDAP'.format(username))
            elif not self.user_details_in_sync(user, ldap_users_diffable[username]) or not self.user_groups_in_sync(user, ldap_users_diffable[username]):
                # Update
                ldap_update_user_details(user, dry_run=self.options['dry_run'])
                ldap_update_user_groups(
                    user,
                    ldap_users_diffable[username],
                    dry_run=self.options['dry_run'],
                    delete_group_memberships=self.options['delete_group_memberships'])

                self.COUNTS['update'] += 1
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('[UPDATED] Inside user {} is out of sync with LDAP'.format(username))
            else:
                # In sync :-)
                self.COUNTS['in_sync'] += 1
                if int(self.options['verbosity']) == 3:
                    self.stdout.write('[OK] Inside user {} is in sync with LDAP'.format(username))

    def log_totals(self):
        if self.COUNTS['create'] > 0 or self.COUNTS['update'] > 0 or int(self.options['verbosity']) >= 2:
            self.stdout.write('Totals: created {}, updated {}, in sync: {}'.format(
                self.COUNTS['create'],
                self.COUNTS['update'],
                self.COUNTS['in_sync']))

    def user_details_in_sync(self, inside_user, ldap_user):
        for attr in self.DIFF_ATTRIBUTES:
            if inside_user[attr] != ldap_user[attr]:
                if int(self.options['verbosity']) >= 2:
                    self.stdout.write('{}: {} (Inside) != {} (LDAP)'.format(
                        inside_user['username'],
                        inside_user[attr],
                        ldap_user[attr]))
                return False

        return True

    def user_groups_in_sync(self, inside_user, ldap_user):
        # Compare set of group names
        inside_groups = set(inside_user['groups'])
        ldap_groups = set(ldap_user['groups'])
        if self.options['delete_group_memberships']:
            in_sync = inside_groups == ldap_groups
            if not in_sync and int(self.options['verbosity']) >= 2:
                self.stdout.write('{}: {} (Inside) != {} (LDAP)'.format(
                    inside_user['username'],
                    ','.join(inside_groups),
                    ','.join(ldap_groups)))
        else:
            missing_groups = inside_groups.difference(ldap_groups)
            in_sync = len(missing_groups) == 0
            if not in_sync and int(self.options['verbosity']) >= 2:
                self.stdout.write('{}: Missing groups in LDAP: {}'.format(','.join(missing_groups)))

        return in_sync