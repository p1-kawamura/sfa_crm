from django.db import models

class Testdata(models.Model):
    mitsu_id=models.CharField("見積ID",max_length=10)
    mitsu_num=models.CharField("見積番号",max_length=10)
    mitsu_ver=models.CharField("見積バージョン",max_length=10)
    status=models.CharField("ステータス",max_length=10)
    order_kubun=models.CharField("注文区分",max_length=10)
    use_kubun=models.CharField("利用区分",max_length=10,blank=True)
    use_youto=models.CharField("使用用途",max_length=30,blank=True)
    nouhin_kigen=models.CharField("納品期限日",max_length=10,blank=True)
    nouhin_shitei=models.CharField("納品指定日",max_length=10,blank=True)
    mitsu_day=models.CharField("初回見積日",max_length=10)
    juchu_day=models.CharField("受注日",max_length=10,blank=True)
    hassou_day=models.CharField("発送完了日",max_length=10,blank=True)
    cus_id=models.CharField("顧客ID",max_length=10)
    sei=models.CharField("姓",max_length=10)
    mei=models.CharField("名",max_length=10)
    mail=models.CharField("メール",max_length=50,blank=True)
    pref=models.CharField("都道府県",max_length=10)
    com=models.CharField("会社名",max_length=50,blank=True)
    keiro=models.CharField("流入経路",max_length=10)
    money=models.IntegerField("金額",default=0)
    kakudo=models.CharField("確度",max_length=5,blank=True)
    alert=models.IntegerField("アラート",default=0)

    def __str__(self):
        return self.mitsu_id


class Sfa_action(models.Model):
    mitsu_id=models.CharField("見積ID",max_length=10)
    day=models.CharField("日付",max_length=10)
    type=models.IntegerField("種類",null=False)
    tel_result=models.CharField("TEL結果",max_length=5,blank=True)
    text=models.TextField("内容",blank=True)

    def __str__(self):
        return self.mitsu_id
    
    # type（種類） 1:TEL　2：メール　3：メモ