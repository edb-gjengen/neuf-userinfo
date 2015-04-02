# Installation

    apt-get install libldap2-dev python-dev libmysqlclient-dev libsasl2-dev libldap2-dev libssl-dev ldap-utils redis-server
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    cp userinfosite/settings-sample.py userinfosite/settings.py
    python manage.py syncdb
    python manage.py runserver

## LDAP
    sudo docker run -e LDAP_DOMAIN=neuf.no -e LDAP_ORGANISATION="Neuf" -e LDAP_ADMIN_PWD="toor" -p 389:389 -d nikolaik/openldap
    ldapadd -D "cn=admin,dc=neuf,dc=no" -w "toor" -f test/testdata.ldif  # Testdata
    # Verify import
    ldapsearch -x -b dc=neuf,dc=no
    # Login with test@example.com:test

## Inside
    # create the Inside database tables, if they don't exist already:
    python manage.py syncdb --database=inside

For simple dev you need at least:
    * 1 InsideUser (din_user)
    * 1 InsideGroup (din_group)
    * 1 UserGroupRelationShip (din_usergrouprelationship)

## RADIUS
    # create the radius database tables, if they don't exist already:
    python manage.py syncdb --database=radius

## Homedirs
 - settings.FILESERVER_HOST:~/.ssh/authorized_keys must contain the public key of settings.FILESERVER_USER
 - settings.FILESERVER_USER needs sudo access to FILESERVER_CREATE_HOMEDIR_SCRIPT

# TODO
 - Integrity check view which provides two way diffs for the following:
    - user vs user group
    - user vs kerberos principal
    - user vs auto mount entry
 - Add email addr alias (usernam@s.no, firstname.lastname@s.n)

# External dependencies:
 - LDAP: Read the tutorial on [Howto setup a LDAP server with Docker](https://edb.neuf.no/wiki/index.php?title=Howto_setup_a_LDAP_server_with_Docker)
 - Kerberos: TODO
 - RADIUS: Standard MySQL.
 - Inside: Never going away! See https://git.neuf.no/edb/inside#tab-readme for code and installation
