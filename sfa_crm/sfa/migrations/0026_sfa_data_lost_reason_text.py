# Generated by Django 4.2.1 on 2025-06-30 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0025_sfa_data_lost_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='sfa_data',
            name='lost_reason_text',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='その他の失注理由'),
        ),
    ]
