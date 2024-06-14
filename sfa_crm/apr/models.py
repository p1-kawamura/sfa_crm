from django.db import models


class Approach(models.Model):
    approach_id=models.CharField("アプローチID",max_length=2)
    result=models.CharField("進捗",max_length=2, default=0)
    tel_day=models.CharField("架電日",max_length=255,blank=True,null=True)
    tel_result=models.CharField("対応不在",max_length=255,blank=True,null=True)
    tel_tantou=models.CharField("架電者",max_length=255,blank=True,null=True)
    tel_text=models.CharField("備考",max_length=255,blank=True,null=True)
    mitsu_id=models.CharField("見積ID",max_length=255,blank=True,null=True)
    mitsu_url=models.CharField("見積URL",max_length=255,blank=True,null=True)
    mitsu_num=models.CharField("見積番号",max_length=255,blank=True,null=True)
    mitsu_ver=models.CharField("見積バージョン",max_length=255,blank=True,null=True)
    order_kubun=models.CharField("注文区分",max_length=255,blank=True,null=True)
    juchu_day=models.CharField("受注日",max_length=255,blank=True,null=True)
    busho_id=models.CharField("部署ID",max_length=255,blank=True,null=True)
    busho_name=models.CharField("部署名",max_length=255,blank=True,null=True)
    tantou_id=models.CharField("担当ID",max_length=255,blank=True,null=True)
    tantou_sei=models.CharField("担当姓",max_length=255,blank=True,null=True)
    tantou_mei=models.CharField("担当名",max_length=255,blank=True,null=True)
    tantou_apr_id=models.CharField("連絡担当ID",max_length=255,blank=True,null=True)
    cus_id=models.CharField("顧客ID",max_length=255,blank=True,null=True)
    cus_com=models.CharField("顧客_会社",max_length=255,blank=True,null=True)
    cus_busho=models.CharField("顧客_部署",max_length=255,blank=True,null=True)
    cus_sei=models.CharField("顧客_姓",max_length=255,blank=True,null=True)
    cus_mei=models.CharField("顧客_名",max_length=255,blank=True,null=True)
    cus_tel=models.CharField("顧客_電話",max_length=255,blank=True,null=True)
    cus_mob=models.CharField("顧客_携帯",max_length=255,blank=True,null=True)
    cus_mail=models.CharField("顧客_メール",max_length=255,blank=True,null=True)
    pref=models.CharField("都道府県",max_length=255,blank=True,null=True)
    money=models.IntegerField("金額",blank=True,null=True)
    kakou=models.CharField("加工方法",max_length=255,blank=True,null=True)
    factory=models.CharField("加工場",max_length=255,blank=True,null=True)
    gara=models.CharField("柄名",max_length=255,blank=True,null=True)
    kigen=models.CharField("版期限",max_length=255,blank=True,null=True)

    def __str__(self):
        return self.cus_id
    
    

class Approach_list(models.Model):
    approach_id=models.CharField("アプローチID",max_length=2)
    title=models.CharField("タイトル",max_length=255)
    day=models.CharField("日付",max_length=255)
    action=models.IntegerField("行動",default=0)

    def __str__(self):
        return self.title
    
    # action（追っ掛け）　0:なし　1:あり