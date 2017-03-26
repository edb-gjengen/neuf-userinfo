from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
import logging

from inside import utils
from inside.models import InsideUser, InsideGroup, AuthLog

logger = logging.getLogger(__name__)


class InsideBackend(object):
    """
    Authenticate against the inside database by username, passord or email, password.
    """
    user = None
    inside_user = None

    def authenticate(self, username=None, password=None):
        password_hash = utils.mysql_create(password)
        self.inside_user = InsideUser.objects.filter(
            Q(password=password_hash) & (Q(ldap_username=username) | Q(email=username))
        )
        # TODO log all login attempts
        # AuthLog.objects.create()

        if len(self.inside_user) != 1:
            return None
        self.inside_user = self.inside_user[0]

        try:
            self.user = User.objects.get(username=self.inside_user.ldap_username)
        except User.DoesNotExist:
            # Create a new user.
            self.user = User.objects.create_user(username=self.inside_user.ldap_username)

        # Sync detail and groups from Inside to local Django install (for display and permissions)
        self._update_user_details()
        self.user.save()

        self._update_groups()

        self._update_user_flags()
        self.user.save()

        return self.user

    def _update_user_details(self):
        sync_attrs = ['first_name', 'last_name', 'email']

        for attr in sync_attrs:
            # Copy from Inside user to local Django user
            setattr(self.user, attr, getattr(self.inside_user, attr))

    def _update_groups(self):
        existing_groups = list(self.user.groups.all())
        inside_groups = InsideGroup.objects.filter(user_rels__user=self.inside_user).exclude(posix_group='')
        inside_groups = inside_groups.values_list('posix_group', flat=True)

        # Add new relationships
        for group in inside_groups:
            g, created = Group.objects.get_or_create(name=group)
            self.user.groups.add(g)

        if not settings.INSIDE_AUTH_GROUPS_SYNC_DELETE:
            return

        # Remove old relationships
        for g in existing_groups:
            if g.name not in inside_groups:
                self.user.groups.remove(g)

    def _update_user_flags(self):
        flag_to_group = settings.INSIDE_AUTH_USER_FLAGS_SYNC
        user_groups = self.user.groups.values_list('name', flat=True)
        for flag, group in flag_to_group.iteritems():
            if group in user_groups:
                setattr(self.user, flag, True)
            else:
                setattr(self.user, flag, False)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None