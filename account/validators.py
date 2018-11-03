import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class NumberValidator(object):
    def __init__(self, min_digits=0):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("비밀번호는 적어도 하나의 숫자, 0-9를 포함해야합니다.."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
           # "Your password must contain at least %(min_digits)d digit(s), 0-9." % {'min_digits': self.min_digits}
            "비밀번호는 적어도 하나의 숫자, 0-9를 포함해야합니다.."
        )