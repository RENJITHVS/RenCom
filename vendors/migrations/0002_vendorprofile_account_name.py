# Generated by Django 4.1.1 on 2022-10-19 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='account_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
