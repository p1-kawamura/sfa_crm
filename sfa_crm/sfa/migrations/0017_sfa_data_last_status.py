# Generated by Django 4.2.1 on 2024-05-21 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0016_sfa_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='sfa_data',
            name='last_status',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ステータス最終日'),
        ),
    ]
