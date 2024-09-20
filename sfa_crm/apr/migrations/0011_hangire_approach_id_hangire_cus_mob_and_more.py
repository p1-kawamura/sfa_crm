# Generated by Django 4.2.1 on 2024-09-19 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0010_approach_busho_apr_id_hangire_busho_apr_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='hangire',
            name='approach_id',
            field=models.CharField(default=0, max_length=2, verbose_name='アプローチID'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='cus_mob',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客_携帯'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='cus_mob_search',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客_携帯_検索用'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='cus_tel',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客_電話'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='cus_tel_search',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客_電話_検索用'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='order_kubun',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='注文区分'),
        ),
    ]