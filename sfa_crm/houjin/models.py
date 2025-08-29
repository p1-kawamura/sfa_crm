from django.db import models


class Houjin_gaishou(models.Model):
    recieve_day=models.CharField("受信日時",max_length=255,blank=True,null=True)
    kubun=models.CharField("区分",max_length=255,blank=True,null=True)
    houjin_com=models.CharField("法人_会社",max_length=255,blank=True,null=True)
    houjin_busho=models.CharField("法人_部署",max_length=255,blank=True,null=True)
    houjin_tantou=models.CharField("法人_担当",max_length=255,blank=True,null=True)
    houjin_tel=models.CharField("法人_電話番号",max_length=255,blank=True,null=True)
    houjin_mail=models.CharField("法人_メールアドレス",max_length=255,blank=True,null=True)
    houjin_address=models.CharField("法人_住所",max_length=255,blank=True,null=True)
    houjin_comment=models.TextField("法人_コメント",blank=True,null=True)
    boad_col=models.CharField("ボード_列",max_length=255,default=0)
    boad_row=models.IntegerField("ボード_行",default=0)
    tantou_id=models.CharField("担当ID",max_length=255,blank=True,null=True)
    tantou=models.CharField("担当者",max_length=255,blank=True,null=True)
    bikou=models.TextField("P1備考",blank=True,null=True)
    itaku_result=models.CharField("委託会社_内容",max_length=255,blank=True,null=True)
    itaku_bikou=models.TextField("委託会社_備考",blank=True,null=True)
    last_update=models.CharField("最終更新日",max_length=255,blank=True,null=True)

    def __str__(self):
        return self.houjin_com

