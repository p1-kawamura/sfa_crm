# Generated by Django 4.2.1 on 2024-06-27 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0023_credit_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit_url',
            name='day',
            field=models.CharField(max_length=255, verbose_name='発行日時'),
        ),
    ]
