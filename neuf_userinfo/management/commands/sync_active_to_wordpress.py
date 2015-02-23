from django.conf import settings
from django.core.management.base import BaseCommand
import json
import codecs
import subprocess
import os

from neuf_ldap.models import LdapGroup, LdapUser


class Command(BaseCommand):
    help = 'Syncs users from LDAP to our Wordpress installations'

    def handle(self, *args, **options):
        active_members = LdapGroup.objects.get(name="dns-aktiv").members
        active_users = LdapUser.objects.filter(username__in=active_members)
        users_out = [[u.username, u.first_name, u.last_name, u.email] for u in active_users]

        out_file = codecs.open(settings.WP_OUT_FILENAME, "w+", encoding="utf-8")
        json.dump(users_out, out_file, ensure_ascii=False)
        out_file.close()

        for load_path in settings.WP_LOAD_PATHS:
            cmd = "php {0} {1} {2}".format(
                os.path.join(settings.WP_PHP_SCRIPT_PATH, "import_users.php"),
                settings.WP_OUT_FILENAME,
                load_path
            )
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            script_response = proc.stdout.read()

            if len(script_response) != 0:
                self.stdout.write(script_response)