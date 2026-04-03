from django.db import models


class Web_est(models.Model):
    web_id=models.CharField("問合せ_ID",max_length=255,blank=True,null=True)
    web_num=models.CharField("問合せ_受付番号",max_length=255,blank=True,null=True)
    web_day=models.CharField("問合せ_日時",max_length=255,blank=True,null=True)
    cus_id=models.CharField("顧客_ID",max_length=255,blank=True,null=True)
    cus_sei=models.CharField("顧客_姓",max_length=255,blank=True,null=True)
    cus_mei=models.CharField("顧客_名",max_length=255,blank=True,null=True)
    pref=models.CharField("顧客_都道府県",max_length=255,blank=True,null=True)
    web_kazu=models.IntegerField("問合せ_枚数",default=0)
    mitsu_id=models.CharField("見積_ID",max_length=255,blank=True,null=True)
    mitsu_num=models.CharField("見積_見積番号",max_length=255,blank=True,null=True)
    mitsu_ver=models.CharField("見積_バージョン",max_length=255,blank=True,null=True)
    kubun=models.CharField("注文区分",max_length=255,blank=True,null=True)
    status=models.CharField("ステータス",max_length=255,blank=True,null=True)
    juchu_day=models.CharField("受注日",max_length=255,blank=True,null=True)
    mitsu_kazu=models.IntegerField("見積_枚数",default=0)
    money=models.IntegerField("見積金額",default=0)
    busho_id=models.CharField("部署_ID",max_length=255,blank=True,null=True)
    busho=models.CharField("部署名",max_length=255,blank=True,null=True)
    tantou_id=models.CharField("担当_ID",max_length=255,blank=True,null=True)
    tantou_sei=models.CharField("担当_姓",max_length=255,blank=True,null=True)
    tantou_mei=models.CharField("担当_名",max_length=255,blank=True,null=True)

    def __str__(self):
        return self.web_id
