from django.core.validators import RegexValidator
import re

# Passwords should not contain "
password_re = re.compile(r'(?<!\")', re.IGNORECASE)
PasswordValidator = RegexValidator(password_re, u'Enter a valid password')

username_re = re.compile(r'^[a-z][a-z0-9]*$')  # TODO Length
UsernameValidator = RegexValidator(username_re, u'Enter a valid username')