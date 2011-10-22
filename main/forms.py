from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
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

class LDAPPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        self.users_cache = LdapUser.objects.filter(email=email)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

