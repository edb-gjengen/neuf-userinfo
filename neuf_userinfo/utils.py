# coding: utf-8
from __future__ import unicode_literals
import base64

from neuf_ldap.utils import ldap_create_user
from neuf_radius.utils import radius_create_user
from neuf_userinfo.ssh import create_home_dir
import rijndael
import logging

logger = logging.getLogger(__name__)


def add_new_user(user, dry_run=False):
    """
        - Create new user in LDAP (username, first_name, last_name, email)
        - Add to groups (usergroup, dns-alle), it not exists, create
        - Set LDAP password
        - Create homedir on wii
        - Set RADIUS password
        - (Create automount entry)
        - (Create kerberos principal and set password)
    """
    results = {
        'user': user,
        'ldap_user': ldap_create_user(user, dry_run=dry_run),
        'homedir': create_home_dir(user['username'], dry_run=dry_run),
        # 'ldap_automount': ldap_create_automount(user['username']),  # FIXME disabled
        # 'kerberos_principal': kerberos_create_principal(user['username'], user['password']),  # FIXME disabled
    }
    if user.get('password'):
        results['radius'] = radius_create_user(user['username'], user['password'])

    logger.debug(results)

"""
Rijndael stuff, thank you SO!
Ref: http://stackoverflow.com/questions/8217269/decrypting-strings-in-python-that-were-encrypted-with-mcrypt-rijndael-256-in-php#answers-header
"""

KEY_SIZE = 16
BLOCK_SIZE = 32


def encrypt_rijndael(key, plaintext):
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'

    # could also be one of
    #if len(plaintext) % BLOCK_SIZE != 0:
    #    padded_text = plaintext.ljust((len(plaintext) / BLOCK_SIZE) + 1 * BLOCKSIZE), '\0')
    # -OR-
    #padded_text = plaintext.ljust((len(plaintext) + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE)), '\0')

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])

    encoded = base64.b64encode(ciphertext)

    return encoded


def decrypt_rijndael(key, encoded):
    padded_key = key.ljust(KEY_SIZE, '\0')

    ciphertext = base64.b64decode(encoded)

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])

    plaintext = padded_text.split('\x00', 1)[0]
    return plaintext
