# Generated by Django 4.2.7 on 2023-11-19 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='hashed_verification_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]