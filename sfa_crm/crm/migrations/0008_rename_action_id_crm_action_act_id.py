# Generated by Django 4.2.1 on 2023-08-03 04:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_crm_action_alert_check'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crm_action',
            old_name='action_id',
            new_name='act_id',
        ),
    ]