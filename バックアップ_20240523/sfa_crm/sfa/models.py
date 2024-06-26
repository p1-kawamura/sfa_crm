from django.db import models

class Sfa_data(models.Model):
    mitsu_id=models.CharField("見積ID",max_length=255)
    mitsu_num=models.CharField("見積番号",max_length=255)
    mitsu_ver=models.CharField("見積バージョン",max_length=255)
    mitsu_url=models.CharField("見積URL",max_length=255,blank=True,null=True)
    status=models.CharField("ステータス",max_length=255,blank=True,null=True)
    order_kubun=models.CharField("注文区分",max_length=255,blank=True,null=True)
    use_kubun=models.CharField("利用区分",max_length=255,blank=True,null=True)
    use_youto=models.CharField("使用用途",max_length=255,blank=True,null=True)
    nouhin_kigen=models.CharField("納品期限日",max_length=255,blank=True,null=True)
    nouhin_shitei=models.CharField("納品指定日",max_length=255,blank=True,null=True)
    make_day=models.CharField("見積作成日",max_length=255,blank=True)
    mitsu_day=models.CharField("初回見積日",max_length=255,blank=True,null=True)
    update_day=models.CharField("更新日",max_length=255,blank=True)
    juchu_day=models.CharField("受注日",max_length=255,blank=True,null=True)
    hassou_day=models.CharField("発送完了日",max_length=255,blank=True,null=True)
    cus_id=models.CharField("顧客ID",max_length=255,blank=True,null=True)
    sei=models.CharField("姓",max_length=255,blank=True,null=True)
    mei=models.CharField("名",max_length=255,blank=True,null=True)
    tel=models.CharField("電話番号",max_length=255,blank=True,null=True)
    tel_mob=models.CharField("携帯番号",max_length=255,blank=True,null=True)
    mail=models.CharField("メール",max_length=255,blank=True,null=True)
    pref=models.CharField("都道府県",max_length=255,blank=True,null=True)
    com=models.CharField("会社名",max_length=255,blank=True,null=True)
    com_busho=models.CharField("部課名",max_length=255,blank=True,null=True)
    keiro=models.CharField("流入経路",max_length=255,blank=True,null=True)
    money=models.IntegerField("金額",blank=True,null=True)
    pay=models.CharField("支払方法",max_length=255,blank=True,null=True)
    kakudo=models.CharField("確度",max_length=255,blank=True)
    kakudo_day=models.CharField("予想年月",max_length=255,blank=True,default="")
    bikou=models.TextField("備考",blank=True)
    busho_id=models.CharField("部署ID",max_length=255)
    tantou_id=models.CharField("担当ID",max_length=255)
    show=models.IntegerField("表示",default=0)
    hidden_day=models.CharField("非表示日時",max_length=255,blank=True,default="")
    mw=models.IntegerField("メールワイズ",default=0)
    last_status=models.CharField("ステータス最終日",max_length=255,blank=True,null=True)


    def __str__(self):
        return self.mitsu_id
    
    # show（表示） 0:表示　1：非表示
    # mw（メールワイズ） 0:無し　1：サンクス　2：失注


class Sfa_action(models.Model):
    act_id=models.AutoField("行動ID",primary_key=True)
    mitsu_id=models.CharField("見積ID",max_length=10)
    cus_id=models.CharField("顧客ID",max_length=10,default="")
    day=models.CharField("日付",max_length=10)
    type=models.IntegerField("種類",null=False)
    text=models.TextField("内容",blank=True)
    tel_result=models.CharField("TEL結果",max_length=5,blank=True)
    alert_check=models.IntegerField("アラート",default=0)

    def __str__(self):
        return self.mitsu_id
    
    # type（種類） 1:TEL　2：メール　3：メモ　4：アラート　5：来店


class Member(models.Model):
    busho=models.CharField("部署",max_length=15)
    busho_id=models.CharField("部署ID",max_length=5)
    tantou=models.CharField("担当",max_length=10)
    tantou_id=models.CharField("担当ID",max_length=5)
    last_api=models.CharField("最終API接続",max_length=255,blank=True)

    def __str__(self):
        return self.tantou_id
    

class Sfa_group(models.Model):
    mitsu_id_parent=models.CharField("親ID",max_length=10)
    mitsu_id_child=models.CharField("子ID",max_length=10)

    def __str__(self):
        return self.mitsu_id_child