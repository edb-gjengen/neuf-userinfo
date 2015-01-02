import json, codecs, subprocess, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "userinfosite.settings")
from django.conf import settings

from main.models import *

PHP_SCRIPT_PATH = '/var/www/neuf.no/userinfo/scripts'
OUT_FILENAME = os.path.join(PHP_SCRIPT_PATH,"users_in_group_active.json")

usernames = LdapGroup.objects.get(name="dns-aktiv").usernames
users = LdapUser.objects.filter(username__in=usernames)
users_out = [[u.username,u.first_name,u.last_name,u.email] for u in users]


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
    print script_response,

