# Generated by Django 2.2 on 2019-06-20 10:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0007_auto_20190612_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='ends_at',
            field=models.DateField(default=datetime.date(2019, 7, 20)),
        ),
    ]
