# coding: utf-8
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.validators import MinLengthValidator
from django import forms
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _

from models import *
from validators import PasswordValidator
import utils 

class LDAPSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        # set kerberos password
        set_krb5 = utils.set_kerberos_password(self.user.username, self.cleaned_data['new_password1'])
        
        # set radius password
        set_radius = utils.set_radius_password(self.user.username, self.cleaned_data['new_password1'])

        # set inside password
        set_inside = utils.set_inside_password(self.user.username, self.cleaned_data['new_password1'])

        # Lookup the Ldap user with the identical username (1-to-1).
        self.user = LdapUser.objects.get(username=self.user.username)

        #self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()

        # TODO: Log the result of the above.
        
        return self.user

    def clean_new_password1(self):
        raw_password = self.cleaned_data.get('new_password1')
        # Validation here
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

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user.

        Note: this is the same form as django.contrib.auth.forms.PasswordResetForm
            with some changes for LDAP-lookup.
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])

