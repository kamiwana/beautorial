from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
from .models import *
from .choices import *

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

class BrandForm(forms.ModelForm):
    category = CommaSeparatedSelectInteger(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        required=False,
    )

    class Meta:
        model = Brand
        fields = '__all__'


class ProductForm(forms.ModelForm):
    texture = CommaSeparatedSelectInteger(
        choices=TEXTURE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        required=False,
    )

    class Meta:
        model = Product
        fields = '__all__'