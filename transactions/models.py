import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Account(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)
    holder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default = None)
    account_type_choice = (('active', 'active'), ('passive','savings'))
    account_type = models.CharField(max_length=7, choices=account_type_choice, null=True, blank=True, default = None)
    def __str__(self):
        return self.title
    def balance(self):
        transactions = Transaction.objects.filter(account=self)
        balance = 0
        for transaction in transactions:
            balance += float(transaction.transaction_type+str(transaction.amount))
        return balance
    def date_balance(self, day):
        dt = datetime.datetime.combine(day, datetime.datetime.min.time())
        transactions = Transaction.objects.filter(account=self, created_date__lt=dt)
        date_balance = 0
        for transaction in transactions:
            date_balance += float(transaction.transaction_type+str(transaction.amount))
        return date_balance




class Transaction(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default = None)
    transaction_type_choice = (('-', 'expense'), ('+', 'income'))
    transaction_type = models.CharField(max_length=1, choices=transaction_type_choice)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, default = None)
    amount = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(999999999999.99)], null=True, blank=True, default = 0)
    comment = models.CharField(max_length=200)
    is_initial = models.BooleanField(default=False)
    planned_transaction = models.ForeignKey('planning.MandatoryTransaction', on_delete=models.SET_NULL, null=True, blank=True, default = None)
    def is_planned(self):
        if self.planned_transaction:
            return True
        else:
            return False
    def __str__(self):
        if self.account.account_type == 'active':
            return self.transaction_type+str(self.amount)+ " "+self.comment
        else:
            if self.transaction_type == '+':
                ending = ' Fill up '
            else:
                ending = ' Blow off ' 
            return self.transaction_type+str(self.amount)+ ending +self.account.title