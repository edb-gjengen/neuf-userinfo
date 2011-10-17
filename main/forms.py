from django.contrib.auth.forms import SetPasswordForm
from django.core.validators import MinLengthValidator
from validators import PasswordValidator

from models import *

# not needed?
class LDAPSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        # Lookup the Ldap user with the identical username (1-to-1).
        self.user = LdapUser.objects.get(username=self.user.username)

        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

    def clean_new_password1(self):
        raw_password = self.cleaned_data.get('new_password1')
        # Validation here?
        MinLengthValidator(8)(raw_password)
        PasswordValidator(raw_passwords)
        return raw_password

class LDAPPasswordChangeForm(LDAPSetPasswordForm):
    pass
    #old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    #def clean_old_password(self):
    #    """
    #    Validates that the old_password field is correct.
    #    """
    #    old_password = self.cleaned_data["old_password"]
    #    if not self.user.check_password(old_password):
    #        raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
    #    return old_password
    #
    #PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

