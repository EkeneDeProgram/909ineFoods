# Generated by Django 4.2.7 on 2023-11-22 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0011_remove_category_parent_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='vendor_images/'),
        ),
    ]
