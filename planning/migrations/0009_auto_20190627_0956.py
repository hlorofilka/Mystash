# Generated by Django 2.2 on 2019-06-27 09:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0008_auto_20190620_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='ends_at',
            field=models.DateField(default=datetime.date(2019, 7, 27)),
        ),
    ]
