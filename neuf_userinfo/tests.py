# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from neuf_userinfo.utils import decrypt_rijndael, encrypt_rijndael


class UserSyncTest(TestCase):
    def test_usersync_decode_unicode_password(self):
        usersync_url = reverse('usersync')
        clear_password = 'berombråk123'
        key = settings.INSIDE_USERSYNC_ENC_KEY

        password = encrypt_rijndael(key, clear_password)

        request_params = {
            'api_key': 'lol',
            'firstname': 'a',
            'lastname': 'b',
            'password': password,
            'email': 'a@b.com',
            'username': 'test',
            'groups': 'dns-alle'
        }
        response = self.client.get(usersync_url, request_params)
        self.assertEqual(response.status_code, 200, response)


class RijndaelTest(TestCase):
    def test_decode_unicode_password(self):
        clear_password = 'berombråk123'
        key = settings.INSIDE_USERSYNC_ENC_KEY

        password = encrypt_rijndael(key, clear_password)
        self.assertEqual(decrypt_rijndael(key, password), clear_password)

    def test_decode_ascii_password(self):
        clear_password = 'beromkos123'
        key = settings.INSIDE_USERSYNC_ENC_KEY

        password = encrypt_rijndael(key, clear_password)
        self.assertEqual(decrypt_rijndael(key, password), clear_password)

