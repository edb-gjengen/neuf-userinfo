from django.conf import settings
from fabric.api import settings as fab_settings
from fabric.operations import run
import logging
import os

logger = logging.getLogger(__name__)


def create_home_dir(username):
    """
    Create homedir for username
     - Copy /etc/skel
     - make user
    This use fabric (SSH) for running remote commands

    Ref:
     - http://stackoverflow.com/questions/4888568/can-i-catch-error-codes-when-using-fabric-to-run-calls-in-a-remote-shell
     - http://stackoverflow.com/questions/6741523/using-python-fabric-without-the-command-line-tool-fab
    """
    host = settings.FILESERVER_HOST
    path = os.path.join(settings.FILESERVER_HOME_PATH, username)
    host_string = '{}@{}'.format(settings.FILESERVER_USER, host)

    with fab_settings(host_string=host_string, warn_only=True):
        user_does_not_exist = run('id -u {}'.format(username))
        if user_does_not_exist:
            logger.error("User '{}' does not exist, user must exist in LDAP before creating home dir.".format(username))
            return False

        # FIXME: just sudo with one script sudo('some_command', shell=False) instead?
        path_exists = run('[ -d "{}" ]; echo $?'.format(path))
        if path_exists:
            logger.error("Path '{}:{}' already exists, doing nothing.".format(host, path))
            return False

        run('cp -r /etc/skel {}'.format(path))
        run('chown -R {0}:{0} {1}'.format(username, path))
        run('chmod -R 700 {}'.format(path))

    return True
