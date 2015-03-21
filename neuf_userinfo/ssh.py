from django.conf import settings
from fabric.api import settings as fab_settings
from fabric.operations import sudo
import logging

logger = logging.getLogger(__name__)


def create_home_dir(username, dry_run=False):
    """
    Create homedir for username via shell script on fileserver host

    This use fabric (SSH) for running the remote command

    Ref: http://stackoverflow.com/questions/6741523/using-python-fabric-without-the-command-line-tool-fab
    """
    host_string = '{}@{}'.format(settings.FILESERVER_USER, settings.FILESERVER_HOST)
    path = settings.FILESERVER_HOME_PATH

    with fab_settings(host_string=host_string, warn_only=True):
        script_cmd = '{} {} {}'.format(settings.FILESERVER_CREATE_HOMEDIR_SCRIPT, path, username)

        if dry_run:
            logger.debug('Created homedir on {} with command: {}'.format(host_string, script_cmd))
        else:
            return_val = sudo(script_cmd, shell=False)
            if not return_val:
                return False

    return True
