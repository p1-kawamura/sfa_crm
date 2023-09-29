from django.db import models

class Crm_action(models.Model):
    act_id=models.AutoField("行動ID",primary_key=True)
    cus_id=models.CharField("顧客ID",max_length=10)
    day=models.CharField("日付",max_length=10)
    type=models.IntegerField("種類",null=False)
    text=models.TextField("内容",blank=True)
    tel_result=models.CharField("TEL結果",max_length=5,blank=True)
    alert_check=models.IntegerField("アラート",default=0)

    def __str__(self):
        return self.cus_id
    
    # type（種類） 1:メモ　2：メール　3：メルマガ　4：TEL　5：外商　6：アラート

    

class Customer(models.Model):
    cus_id=models.CharField("顧客ID",max_length=10)
    bikou1=models.TextField("企業情報",default="")
    bikou2=models.TextField("備考",default="")
    grip_busho_id=models.CharField("グリップ部署ID",max_length=10,blank=True)
    grip_tantou_id=models.CharField("グリップ担当者ID",max_length=10,blank=True)
    mw=models.IntegerField("メールワイズ",default=0)
    mw_busho_id=models.CharField("部署ID",max_length=10,blank=True)
    mw_tantou_id=models.CharField("担当ID",max_length=10,blank=True)
    mw_tantou=models.CharField("担当",max_length=10,blank=True)
    mw_com=models.CharField("会社名",max_length=255,blank=True)
    mw_name=models.CharField("氏名",max_length=255,blank=True)
    mw_mail=models.CharField("メール",max_length=255,blank=True)

    def __str__(self):
        return self.cus_id
    
    # mw（メールワイズ） 0:無し　1：作成