# coding: utf-8
from django.core.management.base import BaseCommand

from inside.models import InsideUser
from neuf_ldap.models import LdapUser


class Command(BaseCommand):
    """ Copy all LDAP users password hashes from to Inside users without one """
    def handle(self, *args, **options):
        ldap_user_passwords = dict(LdapUser.objects.values_list('username', 'password'))
        inside_users = InsideUser.objects.filter(ldap_password=None).exclude(ldap_username=None)
        for u in inside_users:
            ldap_password = ldap_user_passwords.get(u.ldap_username)
            if ldap_password is not None:
                u.ldap_password = ldap_password
                u.save(update_fields=['ldap_password'])
