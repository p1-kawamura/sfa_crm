# Generated by Django 4.2.1 on 2024-06-18 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0004_alter_approach_cus_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='approach',
            name='cus_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客URL'),
        ),
        migrations.AlterField(
            model_name='approach',
            name='cus_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客ID'),
        ),
    ]
