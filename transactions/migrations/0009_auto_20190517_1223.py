# Generated by Django 2.2 on 2019-05-17 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0008_auto_20190516_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='holder',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
