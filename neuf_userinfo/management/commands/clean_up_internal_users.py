from django.core.management.base import BaseCommand
from django.db.models import Q

from inside.models import InsideGroup, InsideUser
from neuf_ldap.models import LdapGroup, LdapUser

from optparse import make_option

ACTIVE_USERS_GROUP = 'dns-aktiv'


class Command(BaseCommand):
    # TODO: Actually clean up stuff
    help = 'Clean up stale LDAP/ users not in group dns-aktiv from Inside'
    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run when syncronizing, does not save anything.'
        ),)

    SYNC_GROUP_PREFIX = 'dns-'
    options = {}

    def handle(self, *args, **options):
        self.options = options

        # Get all active user from Inside
        inside_users_diffable = self.get_inside_users_diffable()

        # Get existing users in LDAP
        ldap_users_diffable = self.get_ldap_users_diffable()

        # Are any LDAP users stale?
        self.stale_ldap_users(inside_users_diffable, ldap_users_diffable)

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

    def stale_ldap_users(self, inside_users_diffable, ldap_users_diffable):
        for username, u in ldap_users_diffable.iteritems():
            if username not in inside_users_diffable:
                self.stdout.write('LDAP user {} is not in group {} in Inside'.format(username, ACTIVE_USERS_GROUP))