from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
from django.db import models
import ldapdb.models
import passwd
import datetime

class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """

    connection_name = 'ldap'

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


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

class Radacct(models.Model):
    connection_name = 'radius'

    radacctid = models.BigIntegerField(primary_key=True)
    acctsessionid = models.CharField(max_length=192)
    acctuniqueid = models.CharField(max_length=96)
    username = models.CharField(max_length=192)
    groupname = models.CharField(max_length=192)
    realm = models.CharField(max_length=192, blank=True)
    nasipaddress = models.CharField(max_length=45)
    nasportid = models.CharField(max_length=45, blank=True)
    nasporttype = models.CharField(max_length=96, blank=True)
    acctstarttime = models.DateTimeField(null=True, blank=True)
    acctstoptime = models.DateTimeField(null=True, blank=True)
    acctsessiontime = models.IntegerField(null=True, blank=True)
    acctauthentic = models.CharField(max_length=96, blank=True)
    connectinfo_start = models.CharField(max_length=150, blank=True)
    connectinfo_stop = models.CharField(max_length=150, blank=True)
    acctinputoctets = models.BigIntegerField(null=True, blank=True)
    acctoutputoctets = models.BigIntegerField(null=True, blank=True)
    calledstationid = models.CharField(max_length=150)
    callingstationid = models.CharField(max_length=150)
    acctterminatecause = models.CharField(max_length=96)
    servicetype = models.CharField(max_length=96, blank=True)
    framedprotocol = models.CharField(max_length=96, blank=True)
    framedipaddress = models.CharField(max_length=45)
    acctstartdelay = models.IntegerField(null=True, blank=True)
    acctstopdelay = models.IntegerField(null=True, blank=True)
    xascendsessionsvrkey = models.CharField(max_length=30, blank=True)
    class Meta:
        db_table = u'radacct'

class Radcheck(models.Model):
    connection_name = 'radius'

    username = models.CharField(max_length=192)
    attribute = models.CharField(max_length=192)
    op = models.CharField(max_length=6)
    value = models.CharField(max_length=759)
    class Meta:
        db_table = u'radcheck'

class Radgroupcheck(models.Model):
    connection_name = 'radius'

    groupname = models.CharField(max_length=192)
    attribute = models.CharField(max_length=192)
    op = models.CharField(max_length=6)
    value = models.CharField(max_length=759)

    class Meta:
        db_table = u'radgroupcheck'

class Radgroupreply(models.Model):
    connection_name = 'radius'

    groupname = models.CharField(max_length=192)
    attribute = models.CharField(max_length=192)
    op = models.CharField(max_length=6)
    value = models.CharField(max_length=759)

    class Meta:
        db_table = u'radgroupreply'

class Radpostauth(models.Model):
    connection_name = 'radius'

    username = models.CharField(max_length=192)
    pass_field = models.CharField(max_length=192, db_column='pass')
    reply = models.CharField(max_length=96)
    authdate = models.DateTimeField()

    class Meta:
        db_table = u'radpostauth'

class Radreply(models.Model):
    connection_name = 'radius'

    username = models.CharField(max_length=192)
    attribute = models.CharField(max_length=192)
    op = models.CharField(max_length=6)
    value = models.CharField(max_length=759)

    class Meta:
        db_table = u'radreply'

class Radusergroup(models.Model):
    connection_name = 'radius'

    username = models.CharField(max_length=192)
    groupname = models.CharField(max_length=192)
    priority = models.IntegerField()

    class Meta:
        db_table = u'radusergroup'

