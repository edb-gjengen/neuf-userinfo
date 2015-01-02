from django.contrib.auth.models import User, Group
from django.db import connections


class InsideBackend(object):
    """
    Authenticate against the inside database
    """

    def authenticate(self, username=None, password=None):
        row = None
        cur = connections['inside'].cursor()
        try:
            cur.execute("SELECT id,firstname,lastname,email FROM din_user WHERE password=PASSWORD(%s) AND (username=%s OR email=%s)", [password, username, username])
            row = cur.fetchone()
        except Exception as e:
            # FIXME errorhandling
            print "Auth ERROR: {}".format(e)
            raise e
        finally:
            cur.close()

        if row:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user.
                user = User(username=username, password=password)

            user = self._update_user_details(user, row)  # Saves user object
            user = self._update_groups(user, row)

            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _update_user_details(self, user, row):
        uid, first_name, last_name, email = row
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        return user

    def _update_groups(self, user, user_row):
        groups = None
        cur = connections['inside'].cursor()
        user_id = user_row[0]

        existing_groups = list(user.groups.all())
        try:
            cur.execute("SELECT g.posix_group FROM din_user AS u LEFT JOIN din_usergrouprelationship AS ugr ON u.id = ugr.user_id LEFT JOIN din_group AS g ON ugr.group_id = g.id WHERE u.id = %s AND g.posix_group != ''", (int(user_row[0]),))
            groups = map(lambda x: x[0], cur.fetchall())
            for group in groups:
                g, created = Group.objects.get_or_create(name=group)
                user.groups.add(g)

            # Remove old relationships
            # TODO: if setting is set, not tested
            for g in existing_groups:
                if g.name not in groups:
                    user.groups.remove(g)

        except Exception as e:
            # FIXME errorhandling
            print "ERROR: {}".format(e)
        finally:
            cur.close()

        return user
