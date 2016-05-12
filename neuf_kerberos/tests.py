from datetime import datetime

from django.test import TestCase
from neuf_kerberos.utils import parse_kadmin_result, format_krb5_date


class KerberosTestCase(TestCase):
    kadmin_getprinc_output = """Principal: yolo@NEUF.NO
Expiration date: [never]
Last password change: Tue Sep 01 14:18:10 CEST 2015
Password expiration date: Sun Aug 30 14:18:10 CEST 2020
Maximum ticket life: 7 days 00:00:00
Maximum renewable life: 90 days 00:00:00
Last modified: Tue Sep 01 14:18:10 CEST 2015 (yolo2/admin@EXAMPLE.COM)
Last successful authentication: Sat May 07 19:10:45 CEST 2016
Last failed authentication: Wed Apr 13 20:27:26 CEST 2016
Failed password attempts: 0
Number of keys: 8
Key: vno 37, aes256-cts-hmac-sha1-96
Key: vno 37, arcfour-hmac
Key: vno 37, des3-cbc-sha1
Key: vno 37, des-cbc-crc
Key: vno 37, des-cbc-md5:v4
Key: vno 37, des-cbc-md5:norealm
Key: vno 37, des-cbc-md5:onlyrealm
Key: vno 37, des-cbc-md5:afs3
MKey: vno 1
Attributes: REQUIRES_PRE_AUTH
Policy: default"""

    def test_parse_kadmin_getprinc_output(self):
        princ = parse_kadmin_result(self.kadmin_getprinc_output)
        self.assertIn('Last successful authentication', princ)

    def test_format_datetime(self):
        last_auth = parse_kadmin_result(self.kadmin_getprinc_output)['Last successful authentication']
        d = format_krb5_date(last_auth)
        self.assertEquals(d, datetime(year=2016, month=5, day=7, hour=19, minute=10, second=45).isoformat())
