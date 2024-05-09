# Generated by Django 4.2.1 on 2024-05-09 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0012_customer_cus_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='bikou1',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='bikou2',
        ),
        migrations.AddField(
            model_name='customer',
            name='cus_touroku',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='顧客登録日'),
        ),
        migrations.AddField(
            model_name='customer',
            name='mitsu_last_busho',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='最終見積_部署名'),
        ),
        migrations.AddField(
            model_name='customer',
            name='mitsu_last_busho_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='最終見積_部署ID'),
        ),
        migrations.AddField(
            model_name='customer',
            name='mitsu_last_tantou',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='最終見積_担当名'),
        ),
        migrations.AddField(
            model_name='customer',
            name='mitsu_last_tantou_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='最終見積_担当ID'),
        ),
        migrations.AddField(
            model_name='customer',
            name='taimen',
            field=models.CharField(blank=True, max_length=10, verbose_name='対面'),
        ),
        migrations.AddField(
            model_name='customer',
            name='tel_mob_serch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='携帯番号_検索'),
        ),
        migrations.AddField(
            model_name='customer',
            name='tel_serch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='電話番号_検索'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mw_busho_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='メールワイズ_部署ID'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mw_tantou',
            field=models.CharField(blank=True, max_length=10, verbose_name='メールワイズ_担当名'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mw_tantou_id',
            field=models.CharField(blank=True, max_length=10, verbose_name='メールワイズ_担当ID'),
        ),
    ]
