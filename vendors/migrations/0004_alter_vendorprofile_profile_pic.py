# Generated by Django 4.1.1 on 2022-10-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0003_vendorprofile_document"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendorprofile",
            name="profile_pic",
            field=models.ImageField(
                default="profile_pic.jpg", upload_to="profile_pic/"
            ),
        ),
    ]