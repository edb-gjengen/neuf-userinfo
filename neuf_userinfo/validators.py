from django.core.validators import RegexValidator
import re

# Passwords should not contain "
password_re = re.compile(r'(?<!\")', re.IGNORECASE)
PasswordValidator = RegexValidator(password_re, u'Enter a valid password')
