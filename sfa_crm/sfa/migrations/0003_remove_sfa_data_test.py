# Generated by Django 4.2.1 on 2023-08-28 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0002_sfa_data_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sfa_data',
            name='test',
        ),
    ]