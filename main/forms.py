from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.core.validators import MinLengthValidator
from validators import PasswordValidator

from models import *
import utils 

class LDAPSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        # set kerberos password
        set_krb5 = utils.set_kerberos_password(self.user.username, self.cleaned_data['new_password1'])
        
        # set radius password
        set_radius = utils.set_radius_password(self.user.username, self.cleaned_data['new_password1'])

        # Lookup the Ldap user with the identical username (1-to-1).
        self.user = LdapUser.objects.get(username=self.user.username)

        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()

        # TODO: Log the result of the above.
        
        return self.user

    def clean_new_password1(self):
        raw_password = self.cleaned_data.get('new_password1')
        # Validation here?
        MinLengthValidator(8)(raw_password)
        PasswordValidator(raw_password)
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

