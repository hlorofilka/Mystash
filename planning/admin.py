from django.contrib import admin
from .models import Period, MandatoryTransaction


# Register your models here.
admin.site.register(Period)
admin.site.register(MandatoryTransaction) 

