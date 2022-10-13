# Generated by Django 4.1.1 on 2022-10-09 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_color_productattribute_size_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='author',
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='images/default-image.jpg', upload_to='product_images/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='mrp_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='MRP Price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Your Price'),
        ),
    ]
