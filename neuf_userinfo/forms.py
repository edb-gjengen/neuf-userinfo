# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django import forms
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _

from inside.models import InsideUser
from inside.utils import set_inside_password

from neuf_kerberos.utils import set_kerberos_password
from neuf_radius.utils import set_radius_password
from neuf_ldap.utils import set_ldap_password
from neuf_userinfo.utils import decrypt_rijndael
from neuf_userinfo.validators import PasswordValidator, UsernameValidator


class NeufSetPasswordForm(SetPasswordForm):
    """
        Saves a user password in each of the following services:
        - Inside (all)
        - Kerberos
        - LDAP
        - RADIUS

        Note: self.user is a local Django User object (which does not have a usable password)
    """
    def save(self, commit=True):

        username = self.user.username
        password = self.cleaned_data['new_password1']

        # Membership database
        set_inside_password(username, password)

        # Active services
        set_kerberos_password(username, password)
        set_radius_password(username, password)
        set_ldap_password(username, password)

        return self.user  # Local Django User

    def clean_new_password1(self):
        raw_password = self.cleaned_data.get('new_password1')

        MinLengthValidator(8)(raw_password)
        PasswordValidator(raw_password)

        return raw_password


class NeufPasswordChangeForm(NeufSetPasswordForm):
    pass


class NeufPasswordResetForm(forms.Form):
    EMAIL_ERROR_MSG = "That e-mail address doesn't have an associated user account. Are you sure you've registered?"
    email = forms.EmailField(label=_("Email"), max_length=254)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        self.users_cache = InsideUser.objects.filter(email=email)  # From Membership database (Inside)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_(self.EMAIL_ERROR_MSG))
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.

        Note: this is the same form as django.contrib.auth.forms.PasswordResetForm
            with some changes for looking up a custom user object.
        """
        from django.core.mail import send_mail
        # UserModel = get_user_model()
        # email = self.cleaned_data["email"]
        # active_users = UserModel._default_manager.filter(
        #     email__iexact=email, is_active=True)
        for user in self.users_cache:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            # if not user.has_usable_password():
            #     continue
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

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name, c)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email], html_message=html_email)


class NewUserForm(forms.Form):
    username = forms.CharField(min_length=3, required=True)
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=8, required=True)
    groups = forms.CharField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        UsernameValidator(username)

        return username

    def clean_password(self):
        raw_password = self.cleaned_data['password']
        password = decrypt_rijndael(settings.INSIDE_USERSYNC_ENC_KEY, raw_password)
        PasswordValidator(password)

        return password

    def clean_groups(self):
        groups = self.cleaned_data['groups']
        return groups.strip().split(',')
