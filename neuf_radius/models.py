from django.db import models


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