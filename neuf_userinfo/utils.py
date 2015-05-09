# coding: utf-8
from __future__ import unicode_literals
import base64
import logging

from neuf_kerberos.utils import add_kerberos_principal
from neuf_radius.utils import create_radius_user
import rijndael

logger = logging.getLogger(__name__)


def add_new_user_sync(user):
    """
        - Create kerberos principal and set password
        - Create/set RADIUS user and password
    """
    # Requires raw password
    add_kerberos_principal(user['username'], user['password'])
    create_radius_user(user['username'], user['password'])

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
