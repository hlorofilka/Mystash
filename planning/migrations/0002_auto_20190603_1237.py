# Generated by Django 2.2 on 2019-06-03 12:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='starts_at',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
