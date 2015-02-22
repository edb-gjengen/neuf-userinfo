from django.core.management.base import BaseCommand, CommandError
import json
import codecs
import subprocess
import os

from neuf_ldap.models import LdapGroup, LdapUser


class Command(BaseCommand):
    help = 'Syncs users from LDAP to our Wordpress installations'

    def handle(self, *args, **options):
        PHP_SCRIPT_PATH = '/var/www/neuf.no/userinfo/scripts'
        OUT_FILENAME = os.path.join(PHP_SCRIPT_PATH, "users_in_group_active.json")

        active_members = LdapGroup.objects.get(name="dns-aktiv").members
        active_users = LdapUser.objects.filter(username__in=active_members)
        users_out = [[u.username, u.first_name, u.last_name, u.email] for u in active_users]

        out_file = codecs.open(OUT_FILENAME, "w", encoding="utf-8")
        json.dump(users_out, out_file, ensure_ascii=False)
        out_file.close()

        wp_load_paths = [
            "/var/www/studentersamfundet.no/www/wp/wp-load.php",
            "/var/www/neuf.no/aktivweb/wp-load.php"
        ]
        for load_path in wp_load_paths:
            cmd = "php {0} {1} {2}".format(
                os.path.join(PHP_SCRIPT_PATH, "import_users.php"),
                OUT_FILENAME,
                load_path
            )
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            script_response = proc.stdout.read()

            self.stdout.write(script_response)