# Generated by Django 4.2.1 on 2023-08-31 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0009_alter_sfa_data_busho_id_alter_sfa_data_make_day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_api',
            field=models.CharField(blank=True, max_length=255, verbose_name='最終API接続'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='busho_id',
            field=models.CharField(max_length=255, verbose_name='部署ID'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='com',
            field=models.CharField(blank=True, max_length=255, verbose_name='会社名'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='com_busho',
            field=models.CharField(blank=True, max_length=255, verbose_name='部課名'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='cus_id',
            field=models.CharField(max_length=255, verbose_name='顧客ID'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='hassou_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='発送完了日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='juchu_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='受注日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='kakudo',
            field=models.CharField(blank=True, max_length=255, verbose_name='確度'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='keiro',
            field=models.CharField(max_length=255, verbose_name='流入経路'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mail',
            field=models.CharField(blank=True, max_length=255, verbose_name='メール'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='make_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='見積作成日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mei',
            field=models.CharField(max_length=255, verbose_name='名'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='初回見積日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_id',
            field=models.CharField(max_length=255, verbose_name='見積ID'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_num',
            field=models.CharField(max_length=255, verbose_name='見積番号'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_url',
            field=models.CharField(blank=True, max_length=255, verbose_name='見積URL'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='mitsu_ver',
            field=models.CharField(max_length=255, verbose_name='見積バージョン'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='nouhin_kigen',
            field=models.CharField(blank=True, max_length=255, verbose_name='納品期限日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='nouhin_shitei',
            field=models.CharField(blank=True, max_length=255, verbose_name='納品指定日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='order_kubun',
            field=models.CharField(max_length=255, verbose_name='注文区分'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='pay',
            field=models.CharField(default='', max_length=255, verbose_name='支払方法'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='pref',
            field=models.CharField(max_length=255, verbose_name='都道府県'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='sei',
            field=models.CharField(max_length=255, verbose_name='姓'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='status',
            field=models.CharField(max_length=255, verbose_name='ステータス'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='tantou_id',
            field=models.CharField(max_length=255, verbose_name='担当ID'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='tel',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='電話番号'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='tel_mob',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='携帯番号'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='update_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='更新日'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='use_kubun',
            field=models.CharField(blank=True, max_length=255, verbose_name='利用区分'),
        ),
        migrations.AlterField(
            model_name='sfa_data',
            name='use_youto',
            field=models.CharField(blank=True, max_length=255, verbose_name='使用用途'),
        ),
    ]