# Generated by Django 4.2.1 on 2024-06-11 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0030_approach_list_action'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Approach',
        ),
        migrations.DeleteModel(
            name='Approach_list',
        ),
    ]
