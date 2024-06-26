from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action,Member,Sfa_group
from crm.models import Customer,Crm_action
import csv
import io
import json
import requests
from datetime import date
from django.http import HttpResponse
import urllib.parse
from django.db.models import Sum
import datetime
from django.db.models import Q 
from django_pandas.io import read_frame


def index_api(request):
    if "mitsu_num" not in request.session:
        request.session["mitsu_num"]=[]
    if "search" not in request.session:
        request.session["search"]={}
    if "busho" not in request.session["search"]:
        request.session["search"]["busho"]=""
    if "tantou" not in request.session["search"]:
        request.session["search"]["tantou"]=""
    if "chumon_kubun" not in request.session["search"]:
        request.session["search"]["chumon_kubun"]=""
    if "keiro" not in request.session["search"]:
        request.session["search"]["keiro"]=""
    if "pref" not in request.session["search"]:
        request.session["search"]["pref"]=""
    if "kakudo" not in request.session["search"]:
        request.session["search"]["kakudo"]=""
    if "kakudo_day" not in request.session["search"]:
        request.session["search"]["kakudo_day"]=""
    if "day_type" not in request.session["search"]:
        request.session["search"]["day_type"]="est" 
    if "day_st" not in request.session["search"]:
        request.session["search"]["day_st"]=""
    if "day_ed" not in request.session["search"]:
        request.session["search"]["day_ed"]=""
    if "st" not in request.session["search"]:
        request.session["search"]["st"]=[]
    if "sort_name" not in request.session["search"]:
        request.session["search"]["sort_name"]="make_sort"
    if "sort_jun" not in request.session["search"]:
        request.session["search"]["sort_jun"]="0"
    if "sort_group" not in request.session["search"]:
        request.session["search"]["sort_group"]=""
    if "com" not in request.session["search"]:
        request.session["search"]["com"]=""
    if "cus_sei" not in request.session["search"]:
        request.session["search"]["cus_sei"]=""
    if "cus_mei" not in request.session["search"]:
        request.session["search"]["cus_mei"]=""
    if "s_mitsu" not in request.session["search"]:
        request.session["search"]["s_mitsu"]=""
    if "alert" not in request.session["search"]:
        request.session["search"]["alert"]=[]
    if "show" not in request.session["search"]:
        request.session["search"]["show"]=[]
    if "page_num" not in request.session["search"]:
        request.session["search"]["page_num"]=1
    if "all_page_num" not in request.session["search"]:
        request.session["search"]["all_page_num"]=""
    if "mw_list" not in request.session:
        request.session["mw_list"]=[]
    if "crm_mw_list" not in request.session:
        request.session["crm_mw_list"]=[]
    if "kakudo_day" not in request.session:
        request.session["kakudo_day"]=datetime.datetime.now().strftime("%Y-%m")
    if "crm_sort" not in request.session:
        request.session["crm_sort"]="0"

    tantou_id=request.session["search"]["tantou"]
    if tantou_id != "":
        last_api=Member.objects.get(tantou_id=tantou_id).last_api
        url="https://core-sys.p1-intl.co.jp/p1web/v1/estimations/?handledById=" + tantou_id + "&updatedAtFrom=" + last_api
        res=requests.get(url)
        res=res.json()
        res=res["estimations"]
        for i in res:
            ins=Sfa_data.objects.filter(mitsu_id=i["id"])
            if (ins.count()==0 and i["status"]=="終了") or i["customerId"]==None:
                continue
            
            # 案件
            Sfa_data.objects.update_or_create(
            mitsu_id=i["id"],
            defaults={
                "mitsu_id":i["id"],
                "mitsu_num":i["number"],
                "mitsu_ver":i["version"],
                "mitsu_url":i["estimationPageUrl"],
                "order_kubun":i["orderType"],
                "use_kubun":i["persona"],
                "use_youto":i["purpose"],
                "nouhin_kigen":i["deliveryLimitDate"],
                "nouhin_shitei":i["deliveryAppointedDate"],
                "make_day":i["createdAt"],
                "mitsu_day":i["firstEstimationDate"],
                "update_day":i["updatedAt"],
                "juchu_day":i["orderReceivedDate"],
                "hassou_day":i["shippedDate"],
                "cus_id":i["customerId"],
                "sei":i["ordererNameLast"],
                "mei":i["ordererNameFirst"],
                "tel":i["ordererTel"],
                "tel_mob":i["ordererMobilePhone"],
                "mail":i["ordererEmailMain"],
                "pref":i["ordererPrefecture"],
                "com":i["ordererCorporateName"],
                "com_busho":i["ordererDepartmentName"],
                "keiro":i["comingRoute"],
                "money":i["totalPrice"],
                "pay":i["paymentMethod"],
                "busho_id":i["handledDepartmentId"],
                "tantou_id":i["handledById"],
                }
            )
            # ステータス
            ins=Sfa_data.objects.get(mitsu_id=i["id"])
            if ins.status not in ["失注","連絡待ち","サンクス"]:
                ins.status=i["status"]
                ins.save()
            if ins.last_status == None and i["status"] in ["終了","キャンセル"]:
                ins.last_status=datetime.datetime.now().strftime("%Y-%m-%d")
                ins.save()


            # 顧客
            if i["customerId"] != None:
                url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + str(i["customerId"])
                res2=requests.get(url2)
                res2=res2.json()

                tel_search=None
                if res2["tel"] != None:
                    tel_search=res2["tel"].replace("-","")
                tel_mob_search=None
                if res2["mobilePhone"] != None:
                    tel_mob_search=res2["mobilePhone"].replace("-","")
                    
                Customer.objects.update_or_create(
                cus_id=res2["id"],
                defaults={
                    "cus_id":res2["id"],
                    "cus_url":res2["customerMstPageUrl"],
                    "com":res2["corporateName"],
                    "com_busho":res2["departmentName"],
                    "sei":res2["nameLast"],
                    "mei":res2["nameFirst"],
                    "pref":res2["prefecture"],
                    "tel":res2["tel"],
                    "tel_search":tel_search,
                    "tel_mob":res2["mobilePhone"],
                    "tel_mob_search":tel_mob_search,
                    "mail":res2["contactEmail"],
                    "mitsu_all":res2["totalEstimations"],
                    "juchu_all":res2["totalReceivedOrders"],
                    "juchu_money":res2["totalReceivedOrdersPrice"],
                    "juchu_last":res2["lastOrderReceivedDate"],
                    }
                )

        # API取得日時
        ins=Member.objects.get(tantou_id=tantou_id)
        ins.last_api=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ins.save()

    return redirect("sfa:index")


def index(request):
    if "mitsu_num" not in request.session:
        request.session["mitsu_num"]=[]
    if "search" not in request.session:
        request.session["search"]={}
    if "busho" not in request.session["search"]:
        request.session["search"]["busho"]=""
    if "tantou" not in request.session["search"]:
        request.session["search"]["tantou"]=""
    if "chumon_kubun" not in request.session["search"]:
        request.session["search"]["chumon_kubun"]=""
    if "keiro" not in request.session["search"]:
        request.session["search"]["keiro"]=""
    if "pref" not in request.session["search"]:
        request.session["search"]["pref"]=""
    if "kakudo" not in request.session["search"]:
        request.session["search"]["kakudo"]=""
    if "kakudo_day" not in request.session["search"]:
        request.session["search"]["kakudo_day"]=""
    if "day_type" not in request.session["search"]:
        request.session["search"]["day_type"]="est" 
    if "day_st" not in request.session["search"]:
        request.session["search"]["day_st"]=""
    if "day_ed" not in request.session["search"]:
        request.session["search"]["day_ed"]=""
    if "st" not in request.session["search"]:
        request.session["search"]["st"]=[]
    if "sort_name" not in request.session["search"]:
        request.session["search"]["sort_name"]="make_sort"
    if "sort_jun" not in request.session["search"]:
        request.session["search"]["sort_jun"]="0"
    if "sort_group" not in request.session["search"]:
        request.session["search"]["sort_group"]=""
    if "com" not in request.session["search"]:
        request.session["search"]["com"]=""
    if "cus_sei" not in request.session["search"]:
        request.session["search"]["cus_sei"]=""
    if "cus_mei" not in request.session["search"]:
        request.session["search"]["cus_mei"]=""
    if "s_mitsu" not in request.session["search"]:
        request.session["search"]["s_mitsu"]=""
    if "alert" not in request.session["search"]:
        request.session["search"]["alert"]=[]
    if "show" not in request.session["search"]:
        request.session["search"]["show"]=[]
    if "page_num" not in request.session["search"]:
        request.session["search"]["page_num"]=1
    if "all_page_num" not in request.session["search"]:
        request.session["search"]["all_page_num"]=""
    if "mw_list" not in request.session:
        request.session["mw_list"]=[]
    if "crm_mw_list" not in request.session:
        request.session["crm_mw_list"]=[]
    if "kakudo_day" not in request.session:
        request.session["kakudo_day"]=datetime.datetime.now().strftime("%Y-%m")
    if "crm_sort" not in request.session:
        request.session["crm_sort"]="0"
    
    ses=request.session["search"]

    # 全体アラート数
    today=str(date.today())
    ins=Sfa_data.objects.filter(tantou_id=ses["tantou"],show=0)
    alert_all=0
    for i in ins:
        h=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=4,alert_check=0,day__lte=today).count()
        alert_all+=h


    # 自動非表示
    kigen=str(date.today() - datetime.timedelta(days=7))
    ins=Sfa_data.objects.filter(tantou_id=ses["tantou"],show=0,last_status__lt=kigen)
    for i in ins:
        i.show=1
        i.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        i.save()


    # フィルター
    fil={}
    fil["tantou_id"]=ses["tantou"]
    if not ses["show"]:
        fil["show"]=0
    if ses["chumon_kubun"] != "":
        fil["order_kubun"]=ses["chumon_kubun"]
    if ses["keiro"] != "":
        fil["keiro"]=ses["keiro"]
    if ses["pref"] != "":
        fil["pref"]=ses["pref"]
    if ses["kakudo"] != "":
        fil["kakudo"]=ses["kakudo"]
    if ses["kakudo_day"] != "":
        fil["kakudo_day"]=ses["kakudo_day"]
    if ses["day_type"]=="est":
        if ses["day_st"] != "":
            fil["make_day__gte"]=ses["day_st"]
        if ses["day_ed"] != "":
            fil["make_day__lte"]=ses["day_ed"]
    else:
        if ses["day_st"] != "":
            fil["hassou_day__gte"]=ses["day_st"]
        if ses["day_ed"] != "":
            fil["hassou_day__lte"]=ses["day_ed"]
    if ses["s_mitsu"] != "":
        fil["mitsu_num"]=ses["s_mitsu"]
    if ses["com"] != "":
        fil["com__contains"]=ses["com"].strip()
    if ses["cus_sei"] != "":
        fil["sei__contains"]=ses["cus_sei"].strip()
    if ses["cus_mei"] != "":
        fil["mei__contains"]=ses["cus_mei"].strip()
    if len(ses["st"])!=0:
        fil["status__in"]=ses["st"]
    
    ins=Sfa_data.objects.filter(**fil)

    # pandasで作り替え
    df=read_frame(ins) 

    # 通常並び替え
    sort_dic={
        "make_sort":"make_day",
        "hassou_sort":"hassou_day",
        "id":"id",
        "money":"money",
        "nouki_sort":"nouki",
        "tel_sort":"tel_last_day",
        "mail_sort":"mail_last_day"
        }
    sort_title=sort_dic[ses["sort_name"]]
    if ses["sort_jun"]=="0":
        asc=True
    else:
        asc=False
    df.sort_values(by=[sort_title,"mitsu_num","mitsu_ver"],inplace=True,ascending=asc)

    # グループ並び替え
    if ses["sort_group"]=="顧客ID":
        try:
            df.sort_values(by=["cus_id","mitsu_num","mitsu_ver"],inplace=True)
        except:
            df.sort_values(by=["com","mitsu_num","mitsu_ver"],inplace=True)
    elif ses["sort_group"]=="見積番号":
        df.sort_values(by=["mitsu_num","mitsu_ver"],inplace=True)


    # # ページネーション
    # result=ins.count()
    # if result == 0:
    #     all_num = 1
    # elif result % 50 == 0:
    #     all_num = result / 50
    # else:
    #     all_num = result // 50 + 1
    # all_num=int(all_num)
    # request.session["search"]["all_page_num"]=all_num
    # num=ses["page_num"]
    # if all_num==1:
    #     num=1
    #     request.session["search"]["page_num"]=1
    # df2=df.iloc[(num-1)*50 : num*50].copy()

    # 一旦全表示
    df2=df.copy()


    # データフレームから直接リスト作成
    list3=[]
    list2=df2.to_dict(orient='index')
    for i,h in list2.items():
        list3.append(h)


    # 詳細作成テスト
    list=[]
    for i in list3:
        dic={}
        dic["id"]=i["id"]
        dic["mitsu_id"]=i["mitsu_id"]
        dic["mitsu_url"]=i["mitsu_url"]
        dic["cus_id"]=i["cus_id"]
        dic["make_day"]=i["make_day"][5:].replace("-","/")
        dic["mitsu_num"]=i["mitsu_num"] + "-" + i["mitsu_ver"]
        dic["order_kubun"]=i["order_kubun"] or ""
        if i["keiro"]!= None:
            dic["keiro"]=i["keiro"][:1]
            if i["keiro"] in ["WEB → 来店","Tel → 来店","来店"]:
                dic["keiro_tempo"]=1        
        if i["use_kubun"] != None:
            dic["use_kubun"]=i["use_kubun"][:1]
        if i["use_youto"] != None:
            d={"チームウェア・アイテム":"チ","制服・スタッフウェア":"制","販促・ノベルティ":"ノ",
            "記念品・贈答品":"記","販売":"販","自分用":"自","その他":"他","":""}
            dic["use_youto"]=d[i["use_youto"]]
        dic["pref"]=i["pref"] or ""
        dic["com"]=i["com"] or ""
        dic["cus"]=(i["sei"] or "") + " " + (i["mei"] or "")
        d={"見積中":"未","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待","サンクス":"サ","":""}
        dic["status"]=d[i["status"]]
        dic["money"]=i["money"]
        if i["nouhin_kigen"] != None:
            dic["nouki"]="期限：" + i["nouhin_kigen"][5:].replace("-","/")
        elif i["nouhin_shitei"] != None:
            dic["nouki"]="指定：" +i["nouhin_shitei"][5:].replace("-","/")
        else:
            dic["nouki"]=""
  
        if i["juchu_day"] != None:
            dic["juchu"]=i["juchu_day"][5:].replace("-","/")
        if i["hassou_day"] != None:
            dic["hassou"]=i["hassou_day"][5:].replace("-","/")

        dic["kakudo"]=i["kakudo"]
        dic["mw"]=i["mw"]
        dic["show"]=i["show"]
        
        # バージョンの同期
        try:
            parent_id=Sfa_group.objects.get(mitsu_id_child=i["mitsu_id"]).mitsu_id_parent
            group_id=parent_id
        except:
            group_id=i["mitsu_id"]

        dic["bikou"]=Sfa_data.objects.get(mitsu_id=group_id).bikou
        memo=Sfa_action.objects.filter(mitsu_id=group_id)
        memo1=""
        memo2=""
        shurui={1:"TEL",2:"メール",3:"メモ",4:"アラート",5:"来店"}
        if memo.count()>0:
            for h in memo:
                if h.text!="":
                    memo1+=h.text + "、"
                memo2+=h.day + " " + shurui[h.type] + " " + h.tel_result + " " + h.text + "\n"
        dic["memo1"]=memo1[:-1]
        dic["memo2"]=memo2

        tel_count=Sfa_action.objects.filter(mitsu_id=group_id,type=1).count() 
        if tel_count > 0:
            act_tel=Sfa_action.objects.filter(mitsu_id=group_id,type=1).latest("day")
            dic["tel"]=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            if act_tel.tel_result=="対応":
                dic["tel_result"]=1
            else:
                dic["tel_result"]=2

        mail_count=Sfa_action.objects.filter(mitsu_id=group_id,type=2).count()
        if mail_count > 0:
            act_mail=Sfa_action.objects.filter(mitsu_id=group_id,type=2).latest("day")
            dic["mail"]=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ") "
            dic["mail_result"]=1
        else:
            dic["mail_result"]=0

        alert_count=Sfa_action.objects.filter(mitsu_id=i["mitsu_id"],type=4,alert_check=0,day__lte=today).count()
        dic["alert"]=alert_count

        list.append(dic)

    # # 詳細作成
    # list=[]
    # for i in ins:
    #     dic={}
    #     dic["id"]=i.id
    #     dic["mitsu_id"]=i.mitsu_id
    #     dic["mitsu_url"]=i.mitsu_url
    #     dic["cus_id"]=i.cus_id
    #     dic["make_day"]=i.make_day[5:].replace("-","/")
    #     dic["make_sort"]=i.make_day
    #     dic["mitsu_num"]=i.mitsu_num + "-" + i.mitsu_ver
    #     dic["order_kubun"]=i.order_kubun or ""
    #     if i.keiro != None:
    #         dic["keiro"]=i.keiro[:1]
    #         if i.keiro in ["WEB → 来店","Tel → 来店","来店"]:
    #             dic["keiro_tempo"]=1        
    #     if i.use_kubun != None:
    #         dic["use_kubun"]=i.use_kubun[:1]
    #     if i.use_youto != None:
    #         d={"チームウェア・アイテム":"チ","制服・スタッフウェア":"制","販促・ノベルティ":"ノ",
    #         "記念品・贈答品":"記","販売":"販","自分用":"自","その他":"他","":""}
    #         dic["use_youto"]=d[i.use_youto]
    #     dic["pref"]=i.pref or ""
    #     dic["com"]=i.com or ""
    #     dic["cus"]=(i.sei or "") + " " + (i.mei or "")
    #     d={"見積中":"未","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待","サンクス":"サ","":""}
    #     dic["status"]=d[i.status]
    #     dic["money"]=i.money
    #     if i.nouhin_kigen != None:
    #         dic["nouki"]="期限：" + i.nouhin_kigen[5:].replace("-","/")
    #         dic["nouki_sort"]=i.nouhin_kigen
    #     elif i.nouhin_shitei != None:
    #         dic["nouki"]="指定：" +i.nouhin_shitei[5:].replace("-","/")
    #         dic["nouki_sort"]=i.nouhin_shitei
    #     else:
    #         dic["nouki"]=""
    #         if ses["sort_jun"]=="0":
    #             dic["nouki_sort"]="2100-01-01"
    #         else:
    #             dic["nouki_sort"]="1900-01-01"
    #     if i.juchu_day != None:
    #         dic["juchu"]=i.juchu_day[5:].replace("-","/")
    #     if i.hassou_day != None:
    #         dic["hassou"]=i.hassou_day[5:].replace("-","/")
    #     if i.hassou_day != None:
    #         dic["hassou_sort"]=i.hassou_day
    #     else:
    #         if ses["sort_jun"]=="0":
    #             dic["hassou_sort"]="2100-01-01"
    #         else:
    #             dic["hassou_sort"]="1900-01-01" 
    #     dic["kakudo"]=i.kakudo
    #     dic["mw"]=i.mw
    #     dic["show"]=i.show
        
    #     # バージョンの同期
    #     try:
    #         parent_id=Sfa_group.objects.get(mitsu_id_child=i.mitsu_id).mitsu_id_parent
    #         group_id=parent_id
    #     except:
    #         group_id=i.mitsu_id

    #     dic["bikou"]=Sfa_data.objects.get(mitsu_id=group_id).bikou
    #     memo=Sfa_action.objects.filter(mitsu_id=group_id)
    #     memo1=""
    #     memo2=""
    #     shurui={1:"TEL",2:"メール",3:"メモ",4:"アラート",5:"来店"}
    #     if memo.count()>0:
    #         for h in memo:
    #             if h.text!="":
    #                 memo1+=h.text + "、"
    #             memo2+=h.day + " " + shurui[h.type] + " " + h.tel_result + " " + h.text + "\n"
    #     dic["memo1"]=memo1[:-1]
    #     dic["memo2"]=memo2

    #     tel_count=Sfa_action.objects.filter(mitsu_id=group_id,type=1).count() 
    #     if tel_count > 0:
    #         act_tel=Sfa_action.objects.filter(mitsu_id=group_id,type=1).latest("day")
    #         dic["tel"]=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
    #         dic["tel_sort"]=act_tel.day
    #         if act_tel.tel_result=="対応":
    #             dic["tel_result"]=1
    #         else:
    #             dic["tel_result"]=2
    #     else:
    #         if ses["sort_jun"]=="0":
    #             dic["tel_sort"]="2100-01-01"
    #         else:
    #             dic["tel_sort"]="1900-01-01"
    #         dic["tel_result"]=0

    #     mail_count=Sfa_action.objects.filter(mitsu_id=group_id,type=2).count()
    #     if mail_count > 0:
    #         act_mail=Sfa_action.objects.filter(mitsu_id=group_id,type=2).latest("day")
    #         dic["mail"]=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ") "
    #         dic["mail_sort"]=act_mail.day
    #         dic["mail_result"]=1
    #     else:
    #         if ses["sort_jun"]=="0":
    #             dic["mail_sort"]="2100-01-01"
    #         else:
    #             dic["mail_sort"]="1900-01-01"
    #         dic["mail_result"]=0

    #     alert_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=4,alert_check=0,day__lte=today).count()
    #     dic["alert"]=alert_count

    #     list.append(dic)
    
    # アラート抽出
    if ses["alert"]:
        for i in list[:]:
            if i["alert"]==0:
                list.remove(i)

    # # 並び替え
    # if ses["sort_jun"]=="0":
    #     list=sorted(list,key=lambda x: (x[ses["sort_name"]],x["mitsu_num"]))
    # else:
    #     list=sorted(list,key=lambda x: (x[ses["sort_name"]],x["mitsu_num"]), reverse=True)

    
    # # グループ並び替え
    # if ses["sort_group"]=="顧客ID":
    #     try:
    #         list=sorted(list,key=lambda x: (x["cus_id"],x["mitsu_num"]))
    #     except:
    #         list=sorted(list,key=lambda x: (x["com"],x["mitsu_num"]))
    # elif ses["sort_group"]=="見積番号":
    #     list=sorted(list,key=lambda x: x["mitsu_num"])

    tantou_list=Member.objects.filter(busho_id=ses["busho"])

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    
    params={
        "list":list,
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":tantou_list,
        "chumon_kubun":["","新規","追加","追加新柄","刷り直し","返金"],
        "keiro_list":["","Web","WEB → 来店","Fax","Tel","Tel → 来店","来店","外商","法人問合せ","即日プリント","アンバサダー","イベント"],
        "kakudo_list":["","A","B","C"],
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "status_list":["見積中","見積送信","イメージ","受注","発送完了","キャンセル","終了","保留","失注","連絡待ち","サンクス"],
        "sort_list":{"make_sort":"見積作成日","hassou_sort":"発送完了日","id":"アプリ取込日","money":"金額","nouki_sort":"納期","tel_sort":"最終TEL","mail_sort":"最終メール"},
        "sort_group_list":["","顧客ID","見積番号"],
        "ses":ses,
        "act_user":act_user,
        "alert_all":alert_all,
    }
    return render(request,"sfa/index.html",params)


# 案件検索
def search(request):
    busho=request.POST["busho"]
    tantou=request.POST["tantou"]
    chumon_kubun=request.POST["chumon_kubun"]
    keiro=request.POST["keiro"]
    pref=request.POST["pref"]
    kakudo=request.POST["kakudo"]
    kakudo_day=request.POST["kakudo_day"]
    day_type=request.POST["day_type"]
    day_st=request.POST["day_st"]
    day_ed=request.POST["day_ed"]
    st=request.POST.getlist("st")
    sort_name=request.POST["sort_name"]
    sort_jun=request.POST["sort_jun"]
    sort_group=request.POST["sort_group"]
    com=request.POST["com"]
    cus_sei=request.POST["cus_sei"]
    cus_mei=request.POST["cus_mei"]
    s_mitsu=request.POST["s_mitsu"]
    alert=request.POST.getlist("alert")
    s_mitsu=request.POST["s_mitsu"]
    show=request.POST.getlist("no_show")
    

    request.session["search"]["busho"]=busho
    request.session["search"]["tantou"]=tantou
    request.session["search"]["chumon_kubun"]=chumon_kubun
    request.session["search"]["keiro"]=keiro
    request.session["search"]["pref"]=pref
    request.session["search"]["kakudo"]=kakudo
    request.session["search"]["kakudo_day"]=kakudo_day
    request.session["search"]["day_type"]=day_type
    request.session["search"]["day_st"]=day_st
    request.session["search"]["day_ed"]=day_ed
    request.session["search"]["st"]=st
    request.session["search"]["sort_name"]=sort_name
    request.session["search"]["sort_jun"]=sort_jun
    request.session["search"]["sort_group"]=sort_group
    request.session["search"]["com"]=com
    request.session["search"]["cus_sei"]=cus_sei
    request.session["search"]["cus_mei"]=cus_mei
    request.session["search"]["s_mitsu"]=s_mitsu
    request.session["search"]["alert"]=alert
    request.session["search"]["show"]=show
    return redirect("sfa:index")


# 部署選択（対象担当者表示）
def busho_tantou(request):
    busho_id=request.POST.get("busho")
    tantou=list(Member.objects.filter(busho_id=busho_id).values())
    d={"tantou":tantou}
    return JsonResponse(d)


# モーダルで詳細表示
def mitsu_detail_api(request):
    mitsu_id=request.POST.get("mitsu_id")
    try:
        parent_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
        parent_ver=Sfa_data.objects.get(mitsu_id=parent_id).mitsu_ver
    except:
        parent_id=""
        parent_ver=""
    
    version_list=[""]
    mitsu_num=Sfa_data.objects.get(mitsu_id=mitsu_id).mitsu_num
    mitsu_ver_now=Sfa_data.objects.get(mitsu_id=mitsu_id).mitsu_ver
    ins=Sfa_data.objects.filter(mitsu_num=mitsu_num).order_by("mitsu_id")
    for i in ins:
        if i.mitsu_ver != mitsu_ver_now:
            version_list.append(i.mitsu_ver)

    res=list(Sfa_data.objects.filter(mitsu_id=mitsu_id).values())[0]
    for i in res:
        if res[i]==None:
            res[i]=""
    
    if parent_id=="":
        res2=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
        parent_bikou=""
        if Sfa_group.objects.filter(mitsu_id_parent=mitsu_id).count()>0:
            parent_me="yes"
        else:
            parent_me="no"
    else:
        res2=list(Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day").values())
        parent_bikou=Sfa_data.objects.get(mitsu_id=parent_id).bikou
        parent_me="no"

    today=str(date.today())
    alert=Sfa_action.objects.filter(mitsu_id=mitsu_id,type=4,alert_check=0,day__lte=today)
    if alert.count()==0:
        res3=0
        text=""
        alert_num=0
    else:
        res3=1
        for i in alert:
            text=i.text
            alert_num=i.act_id
    d={
        "res":res,
        "res2":res2,
        "res3":res3,
        "text":text,
        "alert_num":alert_num,
        "parent_id":parent_id,
        "parent_ver":parent_ver,
        "parent_bikou":parent_bikou,
        "parent_me":parent_me,
        "version_list":version_list,
        }
    return JsonResponse(d)


# モーダル上部（確度、ステータス）
def modal_top(request):
    mitsu_id=request.POST.get("mitsu_id")
    parent_id=request.POST.get("parent_id")
    kakudo=request.POST.get("kakudo")
    kakudo_day=request.POST.get("kakudo_day")
    status=request.POST.get("status")
    bikou=request.POST.get("bikou")
    # 備考以外
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.kakudo_day=kakudo_day
    ins.status=status
    if status in ["終了","キャンセル","失注","サンクス"] and ins.last_status==None:
        ins.last_status=datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        ins.last_status=None
    ins.save()
    # 備考
    if parent_id == "":
        ins.bikou=bikou
        ins.save()
    else:
        ins2=Sfa_data.objects.get(mitsu_id=parent_id)
        ins2.bikou=bikou
        ins2.save()
    d={}
    return JsonResponse(d)


# モーダル下部（電話、メール、備考、アラート）
def modal_bot(request):
    act_id=request.POST.get("act_id")
    mitsu_id=request.POST.get("mitsu_id")
    parent_id=request.POST.get("parent_id")
    cus_id=request.POST.get("cus_id")
    day=request.POST.get("day")
    type=request.POST.get("type")
    tel_result=request.POST.get("tel_result")
    text=request.POST.get("text")
    if parent_id != "":
        mitsu_id=parent_id

    if act_id =="":
        if type=="1":
            Sfa_action.objects.create(mitsu_id=mitsu_id,cus_id=cus_id,day=day,type=type,tel_result=tel_result,text=text)
        else:
            Sfa_action.objects.create(mitsu_id=mitsu_id,cus_id=cus_id,day=day,type=type,text=text)
    else:
        ins=Sfa_action.objects.get(act_id=act_id)
        ins.type=type
        ins.day=day
        if type=="1":
            ins.tel_result=tel_result
        ins.text=text
        ins.save()

    # 最終コンタクト日
    if type=="2" or (type=="1" and tel_result=="対応") or type=="5":
        try:
            cus=Customer.objects.get(cus_id=cus_id)
            contact=cus.contact_last
            if contact==None or contact<day:
                cus.contact_last = day
                cus.save()
            # 来店
            if type=="5":
                Crm_action.objects.create(cus_id=cus_id,day=day,type=7,text=text)
        except:
            pass

    res=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
    d={"res":res}
    return JsonResponse(d)


# モーダル下部_クリック
def modal_bot_click(request):
    act_id=request.POST.get("act_id")
    ins=Sfa_action.objects.get(act_id=act_id)
    res={"type":ins.type,"tel":ins.tel_result,"day":ins.day,"text":ins.text}
    d={"res":res}
    return JsonResponse(d)


# モーダル下部_削除
def modal_bot_delete(request):
    act_id=request.POST.get("act_id")
    mitsu_id=request.POST.get("mitsu_id")
    parent_id=request.POST.get("parent_id")
    Sfa_action.objects.get(act_id=act_id).delete()
    if parent_id != "":
        mitsu_id=parent_id
    res=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
    d={"res":res}
    return JsonResponse(d)


# モーダル_アラート解除
def modal_alert_check(request):
    alert_num=request.POST.get("alert_num")
    ins=Sfa_action.objects.get(act_id=alert_num)
    ins.alert_check=1
    ins.save()
    d={}
    return JsonResponse(d)


# モーダル_同期
def modal_group_click(request):
    mitsu_id=request.POST.get("mitsu_id")
    mitsu_num=request.POST.get("mitsu_num")
    parent_ver=request.POST.get("parent_ver")
    if parent_ver=="":
        Sfa_group.objects.get(mitsu_id_child=mitsu_id).delete()
        res=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
        d={"res":res}
    else:
        parent_id=Sfa_data.objects.get(mitsu_num=mitsu_num,mitsu_ver=parent_ver).mitsu_id
        if Sfa_group.objects.filter(mitsu_id_child=parent_id).count()>0:
            parent_id=Sfa_group.objects.get(mitsu_id_child=parent_id).mitsu_id_parent
        Sfa_group.objects.update_or_create(
            mitsu_id_child=mitsu_id,
            defaults={
                "mitsu_id_child":mitsu_id,
                "mitsu_id_parent":parent_id,
            }
        )
        res=list(Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day").values())
        d={"res":res}

    return JsonResponse(d)


# CRMボタン
def kokyaku_detail_api(request):
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    d={}
    return JsonResponse(d)


# 案件表示_検索から
def show_search(request):
    request.session["mitsu_num"]=request.POST["mitsu_num"]
    return redirect("sfa:show")


# 案件表示_モーダルから
def show_direct(request):
    mitsu_id=request.POST["mitsu_id"]
    mitsu_num=Sfa_data.objects.get(mitsu_id=mitsu_id).mitsu_num
    request.session["mitsu_num"]=mitsu_num
    d={}
    return JsonResponse(d)


# 案件表示_設定
def show_settei(request):
    dic=request.POST.get("dic")
    dic=json.loads(dic)
    for key,value in dic.items():
        ins=Sfa_data.objects.get(mitsu_id=key)
        if value:
            ins.show=0
            ins.hidden_day=""
            ins.last_status=None
        else:
            ins.show=1
            ins.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ins.save()
    d={}
    return JsonResponse(d)


# 案件表示_初期ページ
def show_index(request):
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/show.html",{"act_user":act_user})


# 案件表示_結果ページ
def show(request):
    mitsu_num=request.session["mitsu_num"]
    tantou_id=request.session["search"]["tantou"]
    ins=Sfa_data.objects.filter(mitsu_num=mitsu_num,tantou_id=tantou_id).order_by("mitsu_ver")
    if ins.count()>0:
        for i in ins:
            com=i.com or ""
            name=(i.sei or "") +" " + (i.mei or "")
            break
    else:
        com=""
        name=""
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/show.html",{"list":ins,"mitsu_num":mitsu_num,"com":com,"name":name,"act_user":act_user})


# メールワイズ_表示ページ
def mw_page(request):
    busho_id=request.session["search"]["busho"]
    tantou_id=request.session["search"]["tantou"]
    arr={"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    busho=arr[busho_id]
    if tantou_id in ["62","8","9","43","56"]: # 町山、武藤、新里、田中、小山田
        ans="yes"
    else:
        ans="no"
    ins=Sfa_data.objects.filter(~Q(mw=0),busho_id=busho_id).order_by("tantou_id")
    member=Member.objects.all()
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/mw_csv.html",{"busho":busho,"list":ins,"member":member,"ans":ans,"act_user":act_user})


# メールワイズ_追加
def mw_add(request):
    mw_add_list=request.POST.get("mw_list")
    mw_add_list=json.loads(mw_add_list)
    for i in mw_add_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        if ins.status == "失注":
            ins.mw=2
        else:
            ins.mw=1
        ins.save()
    d={}
    return JsonResponse(d)


# メールワイズ_削除ボタン
def mw_delete(request,pk):
    ins=Sfa_data.objects.get(pk=pk)
    ins.mw=0
    ins.save()
    return redirect("sfa:mw_page")


#メールワイズ_CSV準備
def mw_make(request):
    mw_list=request.POST.get("list")
    mw_list=json.loads(mw_list)
    request.session["mw_list"]=mw_list
    d={}
    return JsonResponse(d)


# メールワイズ_DL
def mw_download(request):
    mw_list=request.session["mw_list"]
    mw_csv=[]
    for i in mw_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        if ins.mw==1:
            a=[
                ins.com or "", #会社
                (ins.sei or "") + (ins.mei or ""), #氏名
                ins.mail or "", #メールアドレス
                Member.objects.get(tantou_id=ins.tantou_id).tantou, #担当
                "サンクス", #区分
            ]
            mw_csv.append(a)
            ins.mw=0
            ins.status="サンクス"
            ins.show=1
            ins.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ins.save()
        else:
            a=[
                ins.com or "", #会社
                (ins.sei or "") + (ins.mei or ""), #氏名
                ins.mail or "", #メールアドレス
                Member.objects.get(tantou_id=ins.tantou_id).tantou, #担当
                "失注", #区分
            ]
            mw_csv.append(a)
            ins.mw=0
            ins.save()
    filename=urllib.parse.quote("案件ベースのメール用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response



# メールワイズ（案件、顧客）_DL_自動
def mw_download_auto(request):
    # 案件
    csv_sfa=[]
    ins=Sfa_data.objects.filter(~Q(mw=0))
    for i in ins:
        ins=Sfa_data.objects.get(mitsu_id=i)
        if ins.mw==1:
            a=[
                ins.com or "", #会社
                (ins.sei or "") + (ins.mei or ""), #氏名
                ins.mail or "", #メールアドレス
                Member.objects.get(tantou_id=ins.tantou_id).tantou, #担当
                "サンクス", #区分
            ]
            csv_sfa.append(a)
            ins.mw=0
            ins.status="サンクス"
            ins.show=1
            ins.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ins.save()
        else:
            a=[
                ins.com or "", #会社
                (ins.sei or "") + (ins.mei or ""), #氏名
                ins.mail or "", #メールアドレス
                Member.objects.get(tantou_id=ins.tantou_id).tantou, #担当
                "失注", #区分
            ]
            csv_sfa.append(a)
            ins.mw=0
            ins.save()
    # 顧客
    csv_crm=[]
    ins2=Customer.objects.filter(mw=1)
    for i in ins2:
        b=[
            i.com or "", #会社
            (i.sei or "") + (i.mei or ""), #氏名
            i.mail or "" , #メールアドレス
            i.mw_tantou,  #担当
            "グリップ" #区分
        ]
        csv_crm.append(b)
        i.mw=0
        i.mw_busho_id=""
        i.mw_tantou_id=""
        i.mw_tantou=""
        i.save()
    # 出力
    csv_all=csv_sfa + csv_crm
    filename=urllib.parse.quote("案件顧客アプリ_MW.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in csv_all:
        writer.writerow(line)
    return response



# 一覧から非表示
def show_list_direct(request):
    show_list=request.POST.get("show_list")
    show_list=json.loads(show_list)
    for i in show_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.show=1
        ins.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ins.save()
    d={}
    return JsonResponse(d)


# 非表示案件一覧
def hidden_index(request):
    tantou_id=request.session["search"]["tantou"]
    ins=Sfa_data.objects.filter(tantou_id=tantou_id,show=1).order_by("hidden_day").reverse()[:300] #直近300件

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/hidden.html",{"list":ins,"act_user":act_user})


# 非表示一覧から再表示
def hidden_list_direct(request):
    hidden_list=request.POST.get("hidden_list")
    hidden_list=json.loads(hidden_list)
    for i in hidden_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.show=0
        ins.hidden_day=""
        ins.last_status=None
        ins.save()
    d={}
    return JsonResponse(d)


# 確度集計
def kakudo_index(request):
    if request.method=="GET":
        kakudo_day=request.session["kakudo_day"]
    else:
        kakudo_day=request.POST["kakudo_day"]
        request.session["kakudo_day"]=kakudo_day

    #全体
    all=[]
    for i in ["A","B","C"]:
        li=[]
        all_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=i,kakudo_day=kakudo_day).count()
        li.append(all_count)
        all_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=i,kakudo_day=kakudo_day).aggregate(Sum("money"))
        if all_money["money__sum"] != None:
            li.append(all_money["money__sum"])
        else:
            li.append(0)
        all.append(li)

    #チーム
    busho_arr={"398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    team={}
    for key,value in busho_arr.items():
        team_li=[]
        for i in ["A","B","C"]:
            li=[]
            team_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=i,busho_id=key,kakudo_day=kakudo_day).count()
            li.append(team_count)
            team_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=i,busho_id=key,kakudo_day=kakudo_day).aggregate(Sum("money"))
            if team_money["money__sum"] != None:
                li.append(team_money["money__sum"])
            else:
                li.append(0)
            team_li.append(li)
        team[value]=team_li

    # 個人
    person={}
    for key,value in busho_arr.items():
        ins=Member.objects.filter(busho_id=key).values_list("tantou_id",flat=True)
        person_li=[]
        for i in ins:
            kaku_li=[]
            kaku_li.append(Member.objects.get(tantou_id=i).tantou)
            for h in ["A","B","C"]:
                li=[]
                person_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=h,tantou_id=i,kakudo_day=kakudo_day).count()
                li.append(person_count)
                person_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ","連絡待ち"],kakudo=h,tantou_id=i,kakudo_day=kakudo_day).aggregate(Sum("money"))
                if person_money["money__sum"] != None:
                    li.append(person_money["money__sum"])
                else:
                    li.append(0)
                kaku_li.append(li)
            person_li.append(kaku_li)
        person[value]=person_li

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={"all":all,"team":team,"person":person,"act_user":act_user,"kakudo_day":kakudo_day}
    return render(request,"sfa/kakudo.html",params)


# 担当者設定_一覧
def member_index(request):
    ins=Member.objects.all().order_by("busho_id","id")
    return render(request,"sfa/member.html",{"list":ins})


# 担当者設定_追加
def member_add(request):
    busho_list={"398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    busho_id=request.POST["busho"]
    busho=busho_list[busho_id]
    tantou=request.POST["tantou"]
    tantou_id=request.POST["tantou_id"]
    last_api=request.POST["last_api"] + " 00:00:00"
    if Member.objects.filter(tantou_id=tantou_id).count() >0:
        ans="no"
    else:
        Member.objects.create(busho=busho,busho_id=busho_id,tantou=tantou,tantou_id=tantou_id,last_api=last_api)
        ans="yes"
    ins=Member.objects.all().order_by("busho_id","id")
    return render(request,"sfa/member.html",{"ans":ans,"list":ins})




# 元DB取込
def csv_imp_page(request):
    return render(request,"sfa/csv_imp.html")


def csv_imp(request):

    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    h=0
    for i in csv_list:
        if h!=0:
            Crm_action.objects.create(
                cus_id=i[0],
                day="2024-05-21",
                type=1,
                text=i[1],
                )
        h+=1
        
    # h=0
    # for i in csv_list:
    #     if h!=0:
    #         Sfa_data.objects.update_or_create(
    #             mitsu_id=i[0],
    #             defaults={
    #                 "mitsu_id":i[0],
    #                 "mitsu_num":i[1],
    #                 "mitsu_ver":i[2],
    #                 "status":i[3],
    #                 "order_kubun":i[4],
    #                 "use_kubun":i[5],
    #                 "use_youto":i[6],
    #             }            
    #         )
    #     h+=1

    return render(request,"sfa/csv_imp.html",{"message":"取込が完了しました！"})



# 色々と個別で動かす用
def clear_session(request):
    # request.session.clear()

    ins=Sfa_data.objects.filter(show=0,status__in=["終了","キャンセル","失注","サンクス"])
    for i in ins:
        i.last_status="2024-05-21"
        i.save()
        
    return redirect("sfa:index")