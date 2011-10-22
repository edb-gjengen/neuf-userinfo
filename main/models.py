from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
import ldapdb.models
import passwd
import datetime
class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou=People,dc=neuf,dc=no" # CONFIG
    object_classes = ['inetOrgPerson', 'posixAccount', 'shadowAccount']

    # inetOrgPerson
    first_name = CharField(db_column='givenName')
    last_name = CharField(db_column='sn')
    full_name = CharField(db_column='cn')
    email = CharField(db_column='mail')
    phone = CharField(db_column='telephoneNumber', blank=True)
    mobile_phone = CharField(db_column='mobile', blank=True)
    photo = ImageField(db_column='jpegPhoto')

    # posixAccount
    id = IntegerField(db_column='uidNumber', unique=True) # referenced in reset password form
    group = IntegerField(db_column='gidNumber')
    gecos =  CharField(db_column='gecos')
    home_directory = CharField(db_column='homeDirectory')
    login_shell = CharField(db_column='loginShell', default='/bin/bash')
    username = CharField(db_column='uid', primary_key=True)
    password = CharField(db_column='userPassword')

    # ugly hack to use django internals for password reset
    last_login = datetime.datetime(2001, 1, 1)

    def set_password(self, raw_password):
        if raw_password is None:
            self.password = "!"
        else:
            self.password = passwd.ldap_create(raw_password)
            self.save()

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct.
        """
        return passwd.ldap_validate(raw_password, self.password)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name

class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=Groups,dc=neuf,dc=no" # CONFIG
    object_classes = ['posixGroup']

    # posixGroup attributes
    gid = IntegerField(db_column='gidNumber', unique=True)
    name = CharField(db_column='cn', max_length=200, primary_key=True)
    usernames = ListField(db_column='memberUid')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
