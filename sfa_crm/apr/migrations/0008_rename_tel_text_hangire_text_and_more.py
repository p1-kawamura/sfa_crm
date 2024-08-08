# Generated by Django 4.2.1 on 2024-06-26 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0007_hangire'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hangire',
            old_name='tel_text',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='approach_id',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='cus_busho',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='cus_mob',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='cus_tel',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='factory',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='gara',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='kigen',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='order_kubun',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='tel_day',
        ),
        migrations.RemoveField(
            model_name='hangire',
            name='tel_tantou',
        ),
        migrations.AddField(
            model_name='hangire',
            name='apr_day',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='アプローチ日'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='apr_tantou',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='対応者'),
        ),
        migrations.AddField(
            model_name='hangire',
            name='apr_type',
            field=models.IntegerField(default=0, verbose_name='アプローチ方法'),
        ),
    ]