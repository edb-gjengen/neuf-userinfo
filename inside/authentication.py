from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
import logging

from inside import utils
from inside.models import InsideUser, InsideGroup, AuthLog

logger = logging.getLogger(__name__)


class InsideBackend(object):
    """
    Authenticate against the inside database
    """

    def authenticate(self, username=None, password=None):
        password_hash = utils.mysql_create(password)
        inside_user = InsideUser.objects.filter(
            Q(password=password_hash) & (Q(ldap_username=username) | Q(email=username))
        )
        # TODO log all login attempts
        # AuthLog.objects.create()

        if len(inside_user) != 1:
            return None

        inside_user = inside_user[0]

        try:
            user = User.objects.get(username=inside_user.ldap_username)
        except User.DoesNotExist:
            # Create a new user.
            user = User(username=inside_user.ldap_username, password=password)

        # Sync detail and groups from Inside to local Django install (for display and permissions)
        user = self._update_user_details(user, inside_user)
        user.save()

        user = self._update_groups(user, inside_user)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _update_user_details(self, user, inside_user):
        sync_attrs = {
            'firstname': 'first_name',
            'lastname': 'last_name',
            'email': 'email'
        }
        for inside_attr, local_attr in sync_attrs.iteritems():
            setattr(user, local_attr, getattr(inside_user, inside_attr))

        return user

    def _update_groups(self, user, inside_user):
        existing_groups = list(user.groups.all())
        inside_groups = InsideGroup.objects.filter(user_rels__user=inside_user).exclude(posix_group='')
        inside_groups = inside_groups.values_list('posix_group', flat=True)

        # Add new relationships
        for group in inside_groups:
            g, created = Group.objects.get_or_create(name=group)
            user.groups.add(g)

        if not settings.INSIDE_GROUPS_SYNC_DELETE:
            return user

        # Remove old relationships
        for g in existing_groups:
            if g.name not in inside_groups:
                user.groups.remove(g)

        return user
