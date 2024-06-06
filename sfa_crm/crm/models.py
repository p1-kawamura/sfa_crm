from django.db import models

class Crm_action(models.Model):
    act_id=models.AutoField("行動ID",primary_key=True)
    cus_id=models.CharField("顧客ID",max_length=10)
    day=models.CharField("日付",max_length=10)
    type=models.IntegerField("種類",null=False)
    text=models.TextField("内容",blank=True)
    tel_result=models.CharField("TEL結果",max_length=5,blank=True)
    alert_check=models.IntegerField("アラート",default=0)
    approach_id=models.IntegerField("アプローチID",default=0)

    def __str__(self):
        return self.cus_id
    
    # type（種類） 1:メモ　 2：メール　  3：メルマガ　4：TEL
    #             5：外商　6：アラート　７：来店     8：アプローチリストID

    # approach_id（アプローチID）　0:通常コメント（アプローチリスト以外）

    

class Customer(models.Model):
    cus_id=models.CharField("顧客ID",max_length=10,unique=True)
    cus_url=models.CharField("顧客URL",max_length=255,blank=True,null=True)
    cus_touroku=models.CharField("顧客登録日",max_length=255,blank=True,null=True)
    com=models.CharField("会社名",max_length=255,blank=True,null=True)
    com_busho=models.CharField("部課名",max_length=255,blank=True,null=True)
    sei=models.CharField("姓",max_length=255,blank=True,null=True)
    mei=models.CharField("名",max_length=255,blank=True,null=True)
    pref=models.CharField("都道府県",max_length=255,blank=True,null=True)
    tel=models.CharField("電話番号",max_length=255,blank=True,null=True)
    tel_search=models.CharField("電話番号_検索",max_length=255,blank=True,null=True)
    tel_mob=models.CharField("携帯番号",max_length=255,blank=True,null=True)
    tel_mob_search=models.CharField("携帯番号_検索",max_length=255,blank=True,null=True)
    mail=models.CharField("メール",max_length=255,blank=True,null=True)
    grip_busho_id=models.CharField("グリップ部署ID",max_length=10,blank=True)
    grip_tantou_id=models.CharField("グリップ担当者ID",max_length=10,blank=True)
    mw=models.IntegerField("メールワイズ",default=0)
    mw_busho_id=models.CharField("メールワイズ_部署ID",max_length=10,blank=True)
    mw_tantou_id=models.CharField("メールワイズ_担当ID",max_length=10,blank=True)
    mw_tantou=models.CharField("メールワイズ_担当名",max_length=10,blank=True)
    mitsu_all=models.IntegerField("見積総数",default=0)
    juchu_all=models.IntegerField("受注総数",default=0)
    juchu_money=models.BigIntegerField("受注総金額",default=0)
    mitsu_last=models.CharField("最終見積日",max_length=255,blank=True,null=True)
    mitsu_last_busho_id=models.CharField("最終見積_部署ID",max_length=10,blank=True)
    mitsu_last_busho=models.CharField("最終見積_部署名",max_length=255,blank=True,null=True)
    mitsu_last_tantou_id=models.CharField("最終見積_担当ID",max_length=10,blank=True)
    mitsu_last_tantou=models.CharField("最終見積_担当名",max_length=255,blank=True,null=True)
    juchu_last=models.CharField("最終受注日",max_length=255,blank=True,null=True)
    contact_last=models.CharField("最終コンタクト日",max_length=255,blank=True,null=True)
    taimen=models.CharField("対面",max_length=10,blank=True)
    royal=models.IntegerField("ロイヤル",default=0)

    def __str__(self):
        return self.cus_id
    
    # mw（メールワイズ） 0:無し　1：作成
    # royal（ロイヤル） 0:いいえ　1：はい



class Approach(models.Model):
    approach_id=models.CharField("アプローチID",max_length=2)
    result=models.IntegerField("進捗",default=0)
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
    cus_id=models.CharField("顧客ID",max_length=255,blank=True,null=True)
    cus_com=models.CharField("顧客_会社",max_length=255,blank=True,null=True)
    cus_busho=models.CharField("顧客_部署",max_length=255,blank=True,null=True)
    cus_sei=models.CharField("顧客_姓",max_length=255,blank=True,null=True)
    cus_mei=models.CharField("顧客_名",max_length=255,blank=True,null=True)
    cus_tel=models.CharField("顧客_電話",max_length=255,blank=True,null=True)
    cus_mob=models.CharField("顧客_携帯",max_length=255,blank=True,null=True)
    cus_mail=models.CharField("顧客_メール",max_length=255,blank=True,null=True)
    money=models.IntegerField("金額",blank=True,null=True)
    kakou=models.CharField("加工方法",max_length=255,blank=True,null=True)
    factory=models.CharField("加工場",max_length=255,blank=True,null=True)
    gara=models.CharField("柄名",max_length=255,blank=True,null=True)
    kigen=models.CharField("版期限",max_length=255,blank=True,null=True)

    def __str__(self):
        return self.cus_id
    
    

class Approach_list(models.Model):
    approach_id=models.IntegerField("アプローチID")
    title=models.CharField("タイトル",max_length=255)
    day=models.CharField("日付",max_length=255)

    def __str__(self):
        return self.cus_id