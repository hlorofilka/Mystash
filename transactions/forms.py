import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Transaction


class EditTransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ('created_date', 'transaction_type', 'amount', 'comment')