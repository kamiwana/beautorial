from django import forms
from .models import User
from .choices import *
from django.core.exceptions import ValidationError
from django.core import validators
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import forms as auth_forms

class CommaSeparatedSelectInteger(forms.MultipleChoiceField):
    def to_python(self, value):
        if not value:
            return '0'
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages['invalid_list'], code='invalid_list'
            )
        return ','.join([str(val) for val in value])

    def validate(self, value):
        """
        Validates that the input is a string of integers separeted by comma.
        """
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'], code='required'
            )

        # Validate that each value in the value list is in self.choices.
        for val in value.split(','):
            if not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )


    def prepare_value(self, value):
        """ Convert the string of comma separated integers in list"""
        if value in validators.EMPTY_VALUES:
            return ''
        elif isinstance(value, (list, tuple)):
            return ','.join([str(val) for val in value])
        else:
            return value.split(',')

class UserForm(UserCreationForm):

    icon = CommaSeparatedSelectInteger(
        choices=SKIN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'})
    )

    class Meta:
        model = User
        fields = '__all__'

from django.urls import reverse

class UserChangeForm(forms.ModelForm):
    password = auth_forms.ReadOnlyPasswordHashField(
        label='비밀번호'
    )

    skin_color = CommaSeparatedSelectInteger(
        choices=SKIN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        required=False,
    )

    face_point = CommaSeparatedSelectInteger(
        choices=FACE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        required=False
    )

    favorite_makeup = CommaSeparatedSelectInteger(
        choices=MAKEUP_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        required=False
    )
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = (
            "원본 비밀번호는 저장되지 않으므로 이 사용자의 비밀번호를 알 수 있는 방법은 없습니다. "
            "다만  이 양식으로 <a href=\"%s\"> "
            "<strong>비밀번호를 변경</strong></a>할 수 있습니다."
        ) % reverse('admin:auth_user_password_change', args=[self.instance.id])

        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]