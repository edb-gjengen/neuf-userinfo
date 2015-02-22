from neuf_ldap.models import LdapUser, LdapGroup, LdapAutomountHome
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    user_group = serializers.HyperlinkedIdentityField(view_name='ldapgroup-detail')

    class Meta:
        model = LdapUser
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'user_group')  # 'dn', 'id', 'group',)


class StringListField(serializers.ListField):
    child = serializers.CharField()


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    # members = StringListField()

    class Meta:
        model = LdapGroup
        fields = ('url', 'name',)  # 'dn', 'gid', 'members',)
