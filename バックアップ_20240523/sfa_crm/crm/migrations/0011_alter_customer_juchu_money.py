# Generated by Django 4.2.1 on 2023-10-19 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_customer_contact_last_customer_juchu_all_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='juchu_money',
            field=models.BigIntegerField(default=0, verbose_name='受注総金額'),
        ),
    ]
