# Generated by Django 4.2.7 on 2023-11-20 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0005_vendor_is_login_vendor_registration_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='vendor',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='vendor_locations', to='vendors.vendor'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='vendor_locations', to='vendors.location'),
        ),
    ]
