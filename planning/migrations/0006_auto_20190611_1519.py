# Generated by Django 2.2 on 2019-06-11 15:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0005_auto_20190604_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='ends_at',
            field=models.DateField(default=datetime.date(2019, 7, 11)),
        ),
    ]