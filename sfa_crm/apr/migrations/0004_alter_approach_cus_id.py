# Generated by Django 4.2.1 on 2024-06-18 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0003_alter_approach_list_approach_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approach',
            name='cus_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客URL'),
        ),
    ]
