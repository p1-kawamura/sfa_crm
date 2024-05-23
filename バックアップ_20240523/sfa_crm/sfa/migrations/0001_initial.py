# Generated by Django 4.2.1 on 2023-08-28 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('busho', models.CharField(max_length=15, verbose_name='部署')),
                ('tantou', models.CharField(max_length=10, verbose_name='担当')),
                ('tantou_id', models.CharField(max_length=5, verbose_name='担当ID')),
            ],
        ),
        migrations.CreateModel(
            name='Sfa_action',
            fields=[
                ('act_id', models.AutoField(primary_key=True, serialize=False, verbose_name='行動ID')),
                ('mitsu_id', models.CharField(max_length=10, verbose_name='見積ID')),
                ('day', models.CharField(max_length=10, verbose_name='日付')),
                ('type', models.IntegerField(verbose_name='種類')),
                ('text', models.TextField(blank=True, verbose_name='内容')),
                ('tel_result', models.CharField(blank=True, max_length=5, verbose_name='TEL結果')),
                ('alert_check', models.IntegerField(default=0, verbose_name='アラート')),
            ],
        ),
        migrations.CreateModel(
            name='Sfa_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mitsu_id', models.CharField(max_length=10, verbose_name='見積ID')),
                ('mitsu_num', models.CharField(max_length=10, verbose_name='見積番号')),
                ('mitsu_ver', models.CharField(max_length=10, verbose_name='見積バージョン')),
                ('status', models.CharField(max_length=10, verbose_name='ステータス')),
                ('order_kubun', models.CharField(max_length=10, verbose_name='注文区分')),
                ('use_kubun', models.CharField(blank=True, max_length=10, verbose_name='利用区分')),
                ('use_youto', models.CharField(blank=True, max_length=30, verbose_name='使用用途')),
                ('nouhin_kigen', models.CharField(blank=True, max_length=10, verbose_name='納品期限日')),
                ('nouhin_shitei', models.CharField(blank=True, max_length=10, verbose_name='納品指定日')),
                ('mitsu_day', models.CharField(max_length=10, verbose_name='初回見積日')),
                ('juchu_day', models.CharField(blank=True, max_length=10, verbose_name='受注日')),
                ('hassou_day', models.CharField(blank=True, max_length=10, verbose_name='発送完了日')),
                ('cus_id', models.CharField(max_length=10, verbose_name='顧客ID')),
                ('sei', models.CharField(max_length=10, verbose_name='姓')),
                ('mei', models.CharField(max_length=10, verbose_name='名')),
                ('tel', models.CharField(blank=True, default='', max_length=15, verbose_name='電話番号')),
                ('tel_mob', models.CharField(blank=True, default='', max_length=15, verbose_name='携帯番号')),
                ('mail', models.CharField(blank=True, max_length=50, verbose_name='メール')),
                ('pref', models.CharField(max_length=10, verbose_name='都道府県')),
                ('com', models.CharField(blank=True, max_length=50, verbose_name='会社名')),
                ('keiro', models.CharField(max_length=10, verbose_name='流入経路')),
                ('money', models.IntegerField(default=0, verbose_name='金額')),
                ('pay', models.CharField(default='', max_length=30, verbose_name='支払方法')),
                ('kakudo', models.CharField(blank=True, max_length=5, verbose_name='確度')),
                ('bikou', models.TextField(blank=True, verbose_name='備考')),
                ('busho_id', models.CharField(default='', max_length=5, verbose_name='部署ID')),
                ('tantou_id', models.CharField(default='', max_length=5, verbose_name='担当ID')),
                ('show', models.IntegerField(default=0, verbose_name='表示')),
            ],
        ),
    ]
