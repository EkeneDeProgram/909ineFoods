# Generated by Django 4.2.7 on 2023-11-23 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_order_status_orderitem_order_status_order_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='item',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='order',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderItem',
        ),
        migrations.DeleteModel(
            name='Status',
        ),
    ]
