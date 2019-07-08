import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .models import Transaction, Account
from planning.models import MandatoryTransaction


class EditTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ('created_date', 'transaction_type', 'account', 'amount', 'comment', 'planned_transaction')
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.plans = kwargs.pop("plans")
        super(EditTransactionForm, self).__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(holder=self.request.user).exclude(account_type='passive')
        self.fields["planned_transaction"].queryset = self.plans

class EditSaveUp(ModelForm):
    class Meta:
        model = Transaction
        fields = ('created_date', 'transaction_type', 'account', 'amount')
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EditSaveUp, self).__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(holder=self.request.user, account_type='passive')

        
        
class CreateAccountForm(forms.Form):
    created_date = forms.DateTimeField(initial=timezone.now)
    title = forms.CharField(max_length=200)
    initial_balance = forms.FloatField()
