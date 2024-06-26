from django.db import models

class Sfa_data(models.Model):
    mitsu_id=models.CharField("見積ID",max_length=255,unique=True)
    mitsu_num=models.CharField("見積番号",max_length=255)
    mitsu_ver=models.IntegerField("見積バージョン")
    mitsu_url=models.CharField("見積URL",max_length=255,blank=True,null=True)
    status=models.CharField("ステータス",max_length=255,blank=True,null=True)
    order_kubun=models.CharField("注文区分",max_length=255,blank=True,null=True)
    use_kubun=models.CharField("利用区分",max_length=255,blank=True,null=True)
    use_youto=models.CharField("使用用途",max_length=255,blank=True,null=True)
    nouhin_kigen=models.CharField("納品期限日",max_length=255,blank=True,null=True)
    nouhin_shitei=models.CharField("納品指定日",max_length=255,blank=True,null=True)
    nouki=models.CharField("納期",max_length=255,blank=True,null=True)
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
    tel_last_day=models.CharField("TEL最終日",max_length=255,blank=True,null=True)
    mail_last_day=models.CharField("メール最終日",max_length=255,blank=True,null=True)
    s_status=models.CharField("s_ステータス",max_length=255,blank=True,null=True)
    s_use_youto=models.CharField("s_使用用途",max_length=255,blank=True,null=True)
    s_nouki=models.CharField("s_納期",max_length=255,blank=True,null=True)
    s_make_day=models.CharField("s_見積作成日",max_length=255,blank=True)
    s_juchu_day=models.CharField("s_受注日",max_length=255,blank=True,null=True)
    s_hassou_day=models.CharField("s_発送完了日",max_length=255,blank=True,null=True)
    s_cus_name=models.CharField("s_顧客氏名",max_length=255,blank=True,null=True)
    s_keiro_tempo=models.IntegerField("s_対面あり",default=0)
    s_tel=models.CharField("s_TEL最終日_回数",max_length=255,blank=True,null=True)
    s_tel_result=models.IntegerField("s_TEL色",default=0)
    s_mail=models.CharField("s_メール最終日_回数",max_length=255,blank=True,null=True)
    s_mail_result=models.IntegerField("s_メール色",default=0)
    s_memo1=models.TextField("s_コメント表示用",blank=True,null=True)
    s_memo2=models.TextField("s_コメントポップアップ用",blank=True,null=True)

    def __str__(self):
        return self.mitsu_id
    
    # show（表示） 0:表示　1：非表示
    # mw（メールワイズ） 0:無し　1：サンクス　2：失注
    # s_keiro_tempo（s_対面あり）0:無し　1:あり
    # s_tel_result（s_TEL色）　0:なし　1:対応　2:不在
    # s_mail_result（s_メール色）　0:なし　2:あり




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
    

class Credit_url(models.Model):
    day=models.DateTimeField("発行日",auto_now_add=True)
    tantou=models.CharField("担当",max_length=255)
    meta_data=models.CharField("見積番号",max_length=255)
    money=models.IntegerField("金額",default=0)
    url=models.CharField("URL",max_length=255)

    def __str__(self):
        return self.tantou