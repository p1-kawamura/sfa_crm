# Generated by Django 4.2.1 on 2024-05-30 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_approach_kigen'),
    ]

    operations = [
        migrations.RenameField(
            model_name='approach',
            old_name='moeny',
            new_name='money',
        ),
    ]
