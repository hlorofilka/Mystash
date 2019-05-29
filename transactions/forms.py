import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .models import Transaction, Account


class EditTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ('created_date', 'transaction_type', 'account', 'amount', 'comment')
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EditTransactionForm, self).__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(holder=self.request.user).exclude(account_type='passive')

class CreateAccountForm(forms.Form):
    created_date = forms.DateTimeField(initial=timezone.now)
    title = forms.CharField(max_length=200)
    initial_balance = forms.FloatField()
