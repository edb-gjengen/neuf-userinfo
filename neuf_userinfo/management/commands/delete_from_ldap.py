import distutils
from django.core.management.base import BaseCommand
from optparse import make_option
import os
import sys

from neuf_ldap.models import LdapUser, LdapGroup, LdapAutomountHome


class Command(BaseCommand):
    args = 'filename'
    help = "Takes a file with a newline separated list of usernames and removes matching users (with associated data) from LDAP"
    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run when syncronizing, does not save anything.'
        ),
        make_option(
            '--no-prompt',
            action='store_true',
            dest='no_prompt',
            default=False,
            help='Does not prompt for deletion'
        ),
    )

    options = {}

    def handle(self, *args, **options):
        self.options = options
        if len(args) != 1:
            self.stderr.write('Missing filename')
            sys.exit()

        filename = args[0]
        if not os.path.isfile(filename):
            self.stderr.write('{} is not a file'.format(filename))
            sys.exit()

        with open(filename) as f:
            usernames = f.read().strip().split()
            self.stdout.write('Found {} usernames in file'.format(len(usernames)))

            ldap_users = LdapUser.objects.filter(username__in=usernames)
            self.stdout.write('Matched {} PosixUser objects'.format(ldap_users.count()))
            for user in ldap_users:
                username = user.username
                self.delete_automount_entry(username)
                self.delete_group_memberships(username)
                self.delete_personal_group(username)
                self.delete_ldap_user(user)

    def _user_confirmes_deletion(self, username, object_type):
        if self.options['no_prompt']:
            return True

        val = raw_input('Do you want to permanently remove {} \'{}\'? [y/N]'.format(object_type, username))
        try:
            confirmed = distutils.util.strtobool(val)
        except ValueError:
            confirmed = False

        return confirmed

    def delete_group_memberships(self, username):
        groups_with_memberships = LdapGroup.objects.filter(members__contains=username)
        if groups_with_memberships.count() == 0:
            return

        self.stdout.write('Removing \'{}\' membership in groups: {}'.format(
            username,
            ', '.join(groups_with_memberships.values_list('name', flat=True))))

        if self._user_confirmes_deletion(username, 'PosixGroup membership for'):
            for g in groups_with_memberships:
                if not self.options['dry_run']:
                    g.members.remove(username)
                    g.save()
                    self.stdout.write('Removed PosixGroup membership in {} for \'{}\''.format(g.name, username))

        else:
            self.stdout.write('Did nothing with \'{}\' membership in groups:'.format(
                username,
                ', '.join(groups_with_memberships.values_list('name', flat=True))))

    def delete_personal_group(self, username):
        if self._user_confirmes_deletion(username, 'personal PosixGroup for'):
            if not self.options['dry_run']:
                LdapGroup.objects.filter(name=username).delete()
            self.stdout.write('Removed personal PosixGroup for \'{}\''.format(username))
        else:
            self.stdout.write("Did nothing with personal PosixGroup for \'{}\'".format(username))

    def delete_automount_entry(self, username):
        if self._user_confirmes_deletion(username, 'Automount entry for'):
            if not self.options['dry_run']:
                LdapAutomountHome.objects.filter(username=username).delete()
            self.stdout.write('Removed automount for \'{}\''.format(username))
        else:
            self.stdout.write("Did nothing with automount for \'{}\'".format(username))

    def delete_ldap_user(self, user):
        username = user.username
        if self._user_confirmes_deletion(username, 'PosixUser'):
            if not self.options['dry_run']:
                user.delete()
            self.stdout.write('Removed \'{}\''.format(username))
        else:
            self.stdout.write("Did nothing with \'{}\'".format(username))