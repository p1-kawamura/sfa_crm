# Generated by Django 4.2.1 on 2024-06-14 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='approach',
            name='tantou_apr_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='連絡担当ID'),
        ),
    ]
