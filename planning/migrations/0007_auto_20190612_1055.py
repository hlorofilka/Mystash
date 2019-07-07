# Generated by Django 2.2 on 2019-06-12 10:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0006_auto_20190611_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='ends_at',
            field=models.DateField(default=datetime.date(2019, 7, 12)),
        ),
        migrations.AlterField(
            model_name='period',
            name='goal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]