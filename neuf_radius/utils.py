import hashlib
from neuf_radius.models import Radcheck


def radius_create(raw_password):
    # found in the wild.
    nt_password = hashlib.new('md4', raw_password.encode('utf-16le')).hexdigest()
    return nt_password


def set_radius_password(username, raw_password):
    """
        Set password in Radius mysql backend.
        Create user if one with an NT-Password does not exist.
    """
    pw_type = 'NT-Password'
    radius_defaults = {'attribute': pw_type, 'op': ':='}
    radius_user, created = Radcheck.objects.get_or_create(
        username=username,
        defaults=radius_defaults)

    # Some have clear text passwords!
    if radius_user.attribute != pw_type:
        radius_user.attribute = pw_type

    radius_user.value = radius_create(raw_password)
    radius_user.save()

