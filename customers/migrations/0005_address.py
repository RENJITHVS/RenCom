# Generated by Django 4.1.1 on 2022-10-01 09:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_alter_user_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=150, verbose_name='Full Name')),
                ('phone', models.CharField(max_length=50, verbose_name='Phone Number')),
                ('address_line', models.CharField(max_length=255, verbose_name='Address Line 1')),
                ('city', models.CharField(max_length=150, verbose_name='Town/City/State')),
                ('pincode', models.CharField(max_length=50, verbose_name='Pincode')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('default', models.BooleanField(default=False, verbose_name='Default')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customerprofile', verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
    ]