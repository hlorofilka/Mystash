# Generated by Django 2.2 on 2019-05-29 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0011_auto_20190517_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='account_type',
            field=models.CharField(blank=True, choices=[('active', 'active'), ('passive', 'savings')], default=None, max_length=7, null=True),
        ),
    ]
