from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Transaction(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type_choice = (('-', 'expense'), ('+', 'income'))
    transaction_type = models.CharField(max_length=1, choices=transaction_type_choice)
    amount = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(999999999999.99)],)
    comment = models.CharField(max_length=200)
    def __str__(self):
        return self.transaction_type+str(self.amount)+ " "+self.comment