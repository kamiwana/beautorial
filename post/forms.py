from django import forms
from .models import *
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

class CosmeticChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    cosmetic = forms.ModelMultipleChoiceField(
        queryset=Cosmetic.objects.all(), required=False,widget=FilteredSelectMultiple(
            verbose_name=_('Cosmetic'),
            is_stacked=False
        ))

    class Meta:
        model = StepDetail

    def __init__(self, *args, **kwargs):
        super(CosmeticChangeListForm, self).__init__(*args, **kwargs)

        if self.instance:
          self.fields['cosmetic_set'].initial = self.instance.cosmetic_set.all()

    def save(self, commit=True):
        step_detail = super(CosmeticChangeListForm, self).save(commit=False)

        step_detail.cosmetic_set = self.cleaned_data['cosmetic_set']

        if commit:
            step_detail.save()
            step_detail.save_m2m()

        return step_detail