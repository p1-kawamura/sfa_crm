# Generated by Django 4.2.1 on 2023-09-15 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_remove_grip_com_remove_grip_cus_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cus_id', models.CharField(max_length=10, verbose_name='顧客ID')),
                ('bikou1', models.TextField(default='', verbose_name='企業情報')),
                ('bikou2', models.TextField(default='', verbose_name='備考')),
                ('mw', models.IntegerField(default=0, verbose_name='メールワイズ')),
                ('busho_id', models.CharField(blank=True, max_length=10, verbose_name='部署ID')),
                ('tantou_id', models.CharField(blank=True, max_length=10, verbose_name='担当ID')),
                ('tantou', models.CharField(max_length=10, verbose_name='担当')),
            ],
        ),
    ]