# Generated by Django 4.2.1 on 2024-05-30 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0019_alter_sfa_data_mitsu_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_ver',
            field=models.IntegerField(verbose_name='見積バージョン'),
        ),
    ]
