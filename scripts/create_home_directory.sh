#!/bin/bash
# Usage: $0 <path_to_home_dirs> <username>

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

if [ $# -ne 2 ] ; then
        echo "USAGE $0 <path_to_home_dirs> <username>"
        exit 1
fi

HOME_DIRS_PATH=$1
USERNAME=$2

if ! id -u ${USERNAME} &>/dev/null; then
        echo "Cannot find user ${USERNAME}. Be sure the user is added to the ldap directory before running this script."
        exit 1
fi

if [ -d "${HOME_DIRS_PATH}/${USERNAME}" ] ; then
        echo "Cannot create home directory, it already exists..."
        exit 1
fi

cp -r /etc/skel "${HOME_DIRS_PATH}/${USERNAME}"
chown -R ${USERNAME}:${USERNAME} "${HOME_DIRS_PATH}/${USERNAME}"
chmod -R 751 "${HOME_DIRS_PATH}/${USERNAME}"
