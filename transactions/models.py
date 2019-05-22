from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Account(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)
    holder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default = None)
    def __str__(self):
        return self.title

class Transaction(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, default = None)
    transaction_type_choice = (('-', 'expense'), ('+', 'income'))
    transaction_type = models.CharField(max_length=1, choices=transaction_type_choice)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, default = None)
    amount = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(999999999999.99)], null=True, blank=True, default = 0)
    comment = models.CharField(max_length=200)
    is_initial = models.BooleanField(default=False)
    def __str__(self):
        return self.transaction_type+str(self.amount)+ " "+self.comment