import hashlib
import os
from base64 import encodestring as encode
from base64 import decodestring as decode

# Ref:
#  - http://www.openldap.org/faq/data/cache/347.html
#  - http://www.openldap.org/doc/admin24/security.html

def ldap_create(raw_password, hash_type='ssha'):
    # Generate a salted SHA hash
    salt = os.urandom(4)
    h = hashlib.sha1(raw_password)
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt)[:-1]

def ldap_validate(raw_password, challenge_password):
    # challenge_password is hash from db
    # raw_password is the cleartext password.
    challenge_bytes = decode(challenge_password[6:])
    digest = challenge_bytes[:20]
    salt = challenge_bytes[20:]
    hr = hashlib.sha1(raw_password)
    hr.update(salt)
    return digest == hr.digest()
