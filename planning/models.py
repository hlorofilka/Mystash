import datetime
from django.conf import settings
from django.db import models
from transactions.models import Transaction, Account
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.
class Period(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default = None)
    starts_at = models.DateField(default=datetime.date.today)
    ends_at = models.DateField(default= datetime.date.today() + datetime.timedelta(days=30))
    goal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    def active_money(self):
        money = 0
        act_accounts = Account.objects.filter(holder=self.owner, account_type ='active')
        pas_accounts = Account.objects.filter(holder=self.owner, account_type ='passive')
        for act_account in act_accounts:
            money += act_account.date_balance(self.starts_at)
        for pas_account in pas_accounts:
            money -= pas_account.date_balance(self.starts_at)
        return money

    def at_the_end(self):
        next_day = self.ends_at + datetime.timedelta(days=1)
        money = 0
        act_accounts = Account.objects.filter(holder=self.owner, account_type ='active')
        pas_accounts = Account.objects.filter(holder=self.owner, account_type ='passive')
        for act_account in act_accounts:
            money += act_account.date_balance(next_day)
        for pas_account in pas_accounts:
            money -= pas_account.date_balance(next_day)
        return money

    def completion_rate(self):
        return float(self.at_the_end())/float(self.goal)*100


    def duration(self):
        return (self.ends_at-self.starts_at).days+1
    def free_money(self):
        mandatories = self.mandatorytransaction_set.all()
        free_sum = self.active_money()
        for mandatory in mandatories:
            free_sum += float(mandatory.transaction_type+ str(mandatory.amount))
        return free_sum
    def max_daylimit(self):
        return self.free_money()/self.duration()
    def max_goal(self):
        return self.free_money()
    def daylimit(self):
        return round((self.free_money()-float(self.goal))/self.duration(), 2)
    def is_actual(self):
        return datetime.date.today >= self.starts_at and datetime.date.today <= self.ends_at 
    def __str__(self):
        return self.starts_at.strftime("%d.%m.%Y")+"-"+ self.ends_at.strftime("%d.%m.%Y")+": the goal is "+ str(self.goal)+ " day limit is "+ str(self.daylimit())



class MandatoryTransaction(models.Model):
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name="mandatorytransaction_set")
    title = models.CharField(max_length=200)
    transaction_type_choice = (('-', 'expense'), ('+', 'income'))
    transaction_type = models.CharField(max_length=1, choices=transaction_type_choice)
    amount = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(999999999999.99)], null=True, blank=True, default = 0)
    def money_left(self):
        transactions = self.transaction_set.all()
        balance = self.amount
        for transaction in transactions:
            balance = balance - (transaction.amount)
        return balance

    def is_completed(self):
        if self.money_left() <= 0:
            return True
        else:
            return False

    def __str__(self):
        return self.title+": "+self.transaction_type+str(self.amount)
