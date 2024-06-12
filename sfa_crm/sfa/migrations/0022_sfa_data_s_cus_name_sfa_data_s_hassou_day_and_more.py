# Generated by Django 4.2.1 on 2024-06-12 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0021_sfa_data_show'),
    ]

    operations = [
        migrations.AddField(
            model_name='sfa_data',
            name='s_cus_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_顧客氏名'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_hassou_day',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_発送完了日'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_juchu_day',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_受注日'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_keiro_tempo',
            field=models.IntegerField(default=0, verbose_name='s_対面あり'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_mail',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_メール最終日_回数'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_mail_result',
            field=models.IntegerField(default=0, verbose_name='s_メール色'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_make_day',
            field=models.CharField(blank=True, max_length=255, verbose_name='s_見積作成日'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_memo1',
            field=models.TextField(blank=True, null=True, verbose_name='s_コメント表示用'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_memo2',
            field=models.TextField(blank=True, null=True, verbose_name='s_コメントポップアップ用'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_nouki',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_納期'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_status',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_ステータス'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_tel',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_TEL最終日_回数'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_tel_result',
            field=models.IntegerField(default=0, verbose_name='s_TEL色'),
        ),
        migrations.AddField(
            model_name='sfa_data',
            name='s_use_youto',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='s_使用用途'),
        ),
        migrations.DeleteModel(
            name='Sfa_data_show',
        ),
    ]
