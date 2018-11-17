import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class CustomPasswortValidator(object):
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        #if not re.findall('\d', password):
        #    raise ValidationError(
        #        _("비밀번호는 적어도 하나의 숫자, 0-9를 포함해야합니다.."),
        #        code='password_no_number',
        #    )
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if not any(char.isdigit() for char in password):
            raise ValidationError(_('비밀번호는 적어도  하나의 숫자를 포함해야합니다.') % {'min_length': self.min_digits})
        if not any(char.isalpha() for char in password):
            raise ValidationError(_('비밀번호는 적어도  하나의 영문을 포함해야합니다.') % {'min_length': self.min_digits})
        #if not any(char in special_characters for char in password):
        #    raise ValidationError(_('비밀번호는 적어도  하나의 특수문자를 포함해야합니다.') % {'min_length':self.min_digits})

    def get_help_text(self):
        return ""