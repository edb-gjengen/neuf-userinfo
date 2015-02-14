# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.validators import MinLengthValidator
from django import forms
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _
import sys
from inside.models import InsideUser
from inside.utils import set_inside_password

from models import *
from validators import PasswordValidator
from neuf_userinfo.utils import set_kerberos_password, set_radius_password


class NeufSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):

        # Membership database
        set_inside_password(self.user.username, self.cleaned_data['new_password1'])

        # Active services
        set_kerberos_password(self.user.username, self.cleaned_data['new_password1'])
        set_radius_password(self.user.username, self.cleaned_data['new_password1'])

        # LDAP: Lookup the Ldap user with the identical username (1-to-1).
        self.user = LdapUser.objects.get(username=self.user.username)
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()

        return self.user

    def clean_new_password1(self):
        raw_password = self.cleaned_data.get('new_password1')

        MinLengthValidator(8)(raw_password)
        PasswordValidator(raw_password)

        return raw_password


class NeufPasswordChangeForm(NeufSetPasswordForm):
    pass


class NeufPasswordResetForm(PasswordResetForm):
    EMAIL_ERROR_MSG = "That e-mail address doesn't have an associated user account. Are you sure you've registered?"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        self.users_cache = InsideUser.objects.filter(email=email)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_(self.EMAIL_ERROR_MSG))
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
            if sys.version_info < (2, 6, 6):
                # Workaround for http://bugs.python.org/issue1368247
                email = email.encode('utf-8')

            send_mail(subject, email, from_email, [user.email])
