# Generated by Django 3.1.7 on 2023-07-29 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sfa', '0007_auto_20230729_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdata',
            name='com',
            field=models.CharField(blank=True, max_length=50, verbose_name='会社名'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='hassou_day',
            field=models.CharField(blank=True, max_length=10, verbose_name='発送完了日'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='juchu_day',
            field=models.CharField(blank=True, max_length=10, verbose_name='受注日'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='kakudo',
            field=models.CharField(blank=True, max_length=5, verbose_name='確度'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='mail',
            field=models.CharField(blank=True, max_length=50, verbose_name='メール'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='nouhin_kigen',
            field=models.CharField(blank=True, max_length=10, verbose_name='納品期限日'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='nouhin_shitei',
            field=models.CharField(blank=True, max_length=10, verbose_name='納品指定日'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='use_kubun',
            field=models.CharField(blank=True, max_length=10, verbose_name='利用区分'),
        ),
        migrations.AlterField(
            model_name='testdata',
            name='use_youto',
            field=models.CharField(blank=True, max_length=30, verbose_name='使用用途'),
        ),
    ]
