from django.conf import settings
from django.core.management.base import BaseCommand

from inside.models import InsideGroup, InsideUser

from neuf_ldap.models import LdapGroup, LdapUser
from neuf_ldap.utils import ldap_create_user


class Command(BaseCommand):
    help = 'Syncs users in group dns-aktiv from Inside to LDAP'

    def handle(self, *args, **options):
        # FIXME: Incomplete
        diff_fields = ['username', 'first_name', 'last_name', 'email', 'groups']
        # Get all active user from Inside
        group = InsideGroup.objects.get(posix_name='dns-aktiv')
        inside_users = InsideUser.objects.filter(group_rels__group=group)
        inside_users_diffable = []
        for u in inside_users:
            inside_groups = InsideGroup.objects.filter(user_rels__user=u).exclude(posix_group='')
            inside_groups = inside_groups.values_list('posix_group', flat=True)
            inside_users_diffable.append({
                'username': u.ldap_username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'password': u.ldap_password,
                'email': u.email,
                'groups': inside_groups
            })
        print len(inside_users_diffable)

        # Get existing users in LDAP
        ldap_active_members = LdapGroup.objects.get(name="dns-aktiv").members
        ldap_users = LdapUser.objects.filter(username__in=ldap_active_members)
        ldap_users_diffable = []
        for u in ldap_users:
            ldap_groups = LdapGroup.objects.filter(members__contain=u.username).values_list('name', flat=True)
            ldap_users_diffable.append({
                'username': u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'groups': ldap_groups
            })
        print len(ldap_users_diffable)

        # Diff by username
        # TODO: you are here
        create_users = filter(lambda x: x['username'] not in ldap_users.values_list('username', flat=True),  inside_users)
        for u in create_users:
            pass
            # ldap_create_user(u)

        # update_users = []
        # for u in update_users:
        #     ldap_update_user(u)

        # delete_users = []
        # for u in update_users:
        #     ldap_delete_user(u)