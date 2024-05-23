# Generated by Django 4.2.1 on 2023-09-29 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_crm_action_tel_result'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='busho_id',
            new_name='mw_busho_id',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='com',
            new_name='mw_com',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='mail',
            new_name='mw_mail',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='name',
            new_name='mw_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='tantou',
            new_name='mw_tantou',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='tantou_id',
            new_name='mw_tantou_id',
        ),
        migrations.AddField(
            model_name='customer',
            name='grip_busho_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='グリップ部署ID'),
        ),
        migrations.AddField(
            model_name='customer',
            name='grip_tantou_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='グリップ担当者ID'),
        ),
    ]
