# Generated by Django 4.2.1 on 2024-05-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_crm_action_approach_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='cus_id',
            field=models.CharField(max_length=10, unique=True, verbose_name='顧客ID'),
        ),
    ]
