# Generated by Django 4.2.1 on 2024-06-07 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0026_alter_approach_approach_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approach',
            name='result',
            field=models.CharField(default=0, max_length=2, verbose_name='進捗'),
        ),
        migrations.AlterField(
            model_name='crm_action',
            name='approach_id',
            field=models.CharField(default=0, max_length=2, verbose_name='アプローチID'),
        ),
    ]