# Generated by Django 4.2.1 on 2023-08-03 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20230729_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='crm_action',
            name='alert_check',
            field=models.IntegerField(default=0, verbose_name='アラート'),
        ),
    ]
