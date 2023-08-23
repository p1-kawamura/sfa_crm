from django.db import models

class Crm_action(models.Model):
    act_id=models.AutoField("行動ID",primary_key=True)
    cus_id=models.CharField("顧客ID",max_length=10)
    day=models.CharField("日付",max_length=10)
    type=models.IntegerField("種類",null=False)
    text=models.TextField("内容",blank=True)
    alert_check=models.IntegerField("アラート",default=0)

    def __str__(self):
        return self.cus_id
    
    # type（種類） 1:メモ　2：メール　3：メルマガ　4：TEL　5：外商　6：アラート


class Grip(models.Model):
    cus_id=models.CharField("顧客ID",max_length=10)
    com=models.CharField("会社名",max_length=30,blank=True)
    cus_name=models.CharField("氏名",max_length=20,blank=True)
    pref=models.CharField("都道府県",max_length=50,blank=True)
    mitsu_count=models.IntegerField("見積総数",default=0)
    busho_id=models.CharField("部署ID",max_length=10,blank=True)
    tantou_id=models.CharField("担当者ID",max_length=10,blank=True)

    def __str__(self):
        return self.cus_id