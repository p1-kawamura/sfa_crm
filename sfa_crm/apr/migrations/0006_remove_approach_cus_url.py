# Generated by Django 4.2.1 on 2024-06-19 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0005_approach_cus_url_alter_approach_cus_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approach',
            name='cus_url',
        ),
    ]
