import datetime

from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from .models import Period, MandatoryTransaction

class PeriodForm(ModelForm):
    class Meta:
        model = Period
        exclude = ()

class PeriodGoalForm(forms.Form):
    goal = forms.DecimalField()


class MandatoryTransactionForm(ModelForm):
    class Meta:
        model = MandatoryTransaction
        exclude = ()

MandatoryTransactionFormSet = inlineformset_factory(Period, MandatoryTransaction, form=MandatoryTransactionForm, extra=1)
MandatoryTransactionFormSetEdit = inlineformset_factory(Period, MandatoryTransaction, form=MandatoryTransactionForm, extra=0)
