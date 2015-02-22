from neuf_ldap.models import LdapGroup, LdapUser
from neuf_ldap.serializers import UserSerializer, GroupSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed
    """
    queryset = LdapUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super(UserViewSet, self).get_queryset()

        return LdapUser.objects.filter(username=self.request.user.username)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed
    """
    queryset = LdapGroup.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            member = self.request.QUERY_PARAMS.get('member')
            if member:
                return LdapGroup.objects.filter(members__contains=member)

            return super(GroupViewSet, self).get_queryset()

        return LdapGroup.objects.filter(members__contains=self.request.user.username)