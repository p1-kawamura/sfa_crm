from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action,Member,Sfa_group,Credit_url
from crm.models import Customer,Crm_action
from apr.models import Approach_list,Hangire
import csv
import io
import json
import requests
from datetime import date
from django.http import HttpResponse
import urllib.parse
import datetime
from django.db.models import Q,Sum,Max
from django_pandas.io import read_frame
import pyshorteners


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
        # 操作者
        sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
        sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
        print(sousa_time,sousa_busho,sousa_tantou,"■ API接続")
        
        last_api=Member.objects.get(tantou_id=tantou_id).last_api
        url="https://core-sys.p1-intl.co.jp/p1web/v1/estimations/?handledById=" + tantou_id + "&updatedAtFrom=" + last_api
        res=requests.get(url)
        res=res.json()
        res=res["estimations"]
        for i in res:
            ins=Sfa_data.objects.filter(mitsu_id=i["id"])
            if (ins.count()==0 and i["status"]=="終了") or i["customerId"]==None:
                continue
            
            # ------------------------
            # 案件
            # ------------------------
            s_use_youto=None
            nouki=None
            s_nouki=None
            s_juchu_day=None
            s_hassou_day=None
            s_keiro_tempo=0

            if i["purpose"] != None:
                d={"チームウェア・アイテム":"チ","制服・スタッフウェア":"制","販促・ノベルティ":"ノ","記念品・贈答品":"記","販売":"販","自分用":"自","その他":"他","":""}
                s_use_youto=d[i["purpose"]]

            if i["deliveryAppointedDate"] != None:
                nouki=i["deliveryAppointedDate"]
                s_nouki="指定：" + i["deliveryAppointedDate"][5:].replace("-","/")
            elif i["deliveryLimitDate"] != None:
                nouki=i["deliveryLimitDate"]
                s_nouki="期限：" + i["deliveryLimitDate"][5:].replace("-","/")                

            if i["orderReceivedDate"] != None:
                s_juchu_day=i["orderReceivedDate"][5:].replace("-","/")

            if i["shippedDate"] != None:
                s_hassou_day=i["shippedDate"][5:].replace("-","/")

            if i["comingRoute"] in ["WEB → 来店","Tel → 来店","来店"]:
                s_keiro_tempo=1

            s_cus_name=(i["ordererNameLast"] or "") + " " + (i["ordererNameFirst"] or "")
            s_make_day=i["createdAt"][5:].replace("-","/")

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
                "nouki":nouki,
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
                "s_use_youto":s_use_youto,
                "s_nouki":s_nouki,
                "s_make_day":s_make_day,
                "s_juchu_day":s_juchu_day,
                "s_hassou_day":s_hassou_day,
                "s_cus_name":s_cus_name,
                "s_keiro_tempo":s_keiro_tempo,
                }
            )
            # ステータス
            d={"見積中":"未","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待","サンクス":"サ","":""}
            ins=Sfa_data.objects.get(mitsu_id=i["id"])
            if ins.status not in ["失注","連絡待ち","サンクス"]:
                ins.status=i["status"]
                ins.s_status=d[i["status"]]
                ins.save()

            if ins.last_status == None and i["status"] in ["終了","キャンセル"]:
                ins.last_status=datetime.datetime.now().strftime("%Y-%m-%d")
                ins.save()

            # ------------------------
            # 顧客
            # ------------------------
            url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + str(i["customerId"])
            res2=requests.get(url2)
            res2=res2.json()

            tel_search=None
            if res2["tel"] != None:
                tel_search=res2["tel"].replace("-","")
            tel_mob_search=None
            if res2["mobilePhone"] != None:
                tel_mob_search=res2["mobilePhone"].replace("-","")

            try:
                con_last=Customer.objects.get(cus_id=i["customerId"]).contact_last
                if con_last==None or res2["lastEstimatedAt"]>con_last:
                    contact_last=res2["lastEstimatedAt"]
                else:
                    contact_last=con_last
            except:
                contact_last=res2["lastEstimatedAt"]
                
            Customer.objects.update_or_create(
            cus_id=res2["id"],
            defaults={
                "cus_id":res2["id"],
                "cus_url":res2["customerMstPageUrl"],
                "cus_touroku":res2["createdAt"],
                "com":res2["corporateName"],
                "com_busho":res2["departmentName"],
                "sei":res2["nameLast"],
                "mei":res2["nameFirst"],
                "pref":res2["prefecture"],
                "city":res2["city"],
                "address_1":res2["address1"],
                "address_2":res2["address2"],
                "tel":res2["tel"],
                "tel_search":tel_search,
                "tel_mob":res2["mobilePhone"],
                "tel_mob_search":tel_mob_search,
                "mail":res2["contactEmail"],
                "mitsu_all":res2["totalEstimations"],
                "juchu_all":res2["totalReceivedOrders"],
                "juchu_money":res2["totalReceivedOrdersPrice"],
                "mitsu_last":res2["lastEstimatedAt"],
                "mitsu_last_busho_id":res2["lastHandledDepartmentId"],
                "mitsu_last_busho":res2["lastHandledDepartmentName"],
                "mitsu_last_tantou_id":res2["lastHandledId"],
                "mitsu_last_tantou":res2["lastHandledName"],
                "juchu_last":res2["lastOrderReceivedDate"],
                "contact_last":contact_last,
                "taimen":res2["isVisited"],
                }
            )

        # API取得日時
        ins=Member.objects.get(tantou_id=tantou_id)
        ins.last_api=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ins.save()

        # 自動非表示
        kigen=str(date.today() - datetime.timedelta(days=7))
        ins=Sfa_data.objects.filter(tantou_id=tantou_id,show=0,last_status__lt=kigen)
        for i in ins:
            i.show=1
            i.hidden_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            i.save() 
    
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

   
    # ステータスの件数
    st_fil={}
    st_fil["tantou_id"]=ses["tantou"]
    if not ses["show"]:
        st_fil["show"]=0
    
    st_ins=Sfa_data.objects.filter(**st_fil)
    df_st=read_frame(st_ins) 
    df_st=df_st[["status","id"]].groupby("status").count()
    st_count_list=df_st.to_dict(orient='dict')["id"]
    for i in ["見積中","見積送信","イメージ","受注","発送完了","キャンセル","終了","保留","失注","連絡待ち","サンクス"]:
        if i not in st_count_list:
            st_count_list[i]=0


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


    # アラート
    today=str(date.today())
    cnt=list(Sfa_action.objects.filter(type=4,alert_check=0,day__lte=today).values_list("mitsu_id",flat=True).order_by("mitsu_id").distinct())
    chi_list=list(Sfa_group.objects.filter(mitsu_id_parent__in=cnt).values_list("mitsu_id_child",flat=True))
    cnt += chi_list
    alert_list=list(Sfa_data.objects.filter(**fil, mitsu_id__in=cnt).values_list("mitsu_id",flat=True))
    alert_all=Sfa_data.objects.filter(tantou_id=ses["tantou"],show=0,mitsu_id__in=alert_list).count()

    if ses["alert"]:
        ins=Sfa_data.objects.filter(**fil, mitsu_id__in=cnt)
    
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


    # ページネーション
    result=ins.count()
    if result == 0:
        all_num = 1
    elif result % 100 == 0:
        all_num = result / 100
    else:
        all_num = result // 100 + 1
    all_num=int(all_num)
    request.session["search"]["all_page_num"]=all_num
    num=ses["page_num"]
    if all_num==1:
        num=1
        request.session["search"]["page_num"]=1

    df2=df.iloc[(num-1)*100 : num*100].copy()


    # データフレームから直接リスト作成
    list3=[]
    list2=df2.to_dict(orient='index')
    for i,h in list2.items():
        list3.append(h)


    tantou_list=Member.objects.filter(busho_id=ses["busho"])

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    
    params={
        "list":list3,
        "alert_list":alert_list,
        "st_count_list":st_count_list,
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
        "num":num,
        "all_num":all_num,
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
    request.session["search"]["page_num"]=1

    # 操作者
    tantou_id=request.session["search"]["tantou"]
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
    sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    print(sousa_time,sousa_busho,sousa_tantou,"■ 表示ボタン")

    return redirect("sfa:index")


# ページネーション（前）
def sfa_page_prev(request):
    num=request.session["search"]["page_num"]
    if num-1 > 0:
        request.session["search"]["page_num"] = num - 1
    return redirect("sfa:index")


# ページネーション（最初）
def sfa_page_first(request):
    request.session["search"]["page_num"] = 1
    return redirect("sfa:index")


# ページネーション（次）
def sfa_page_next(request):
    num=request.session["search"]["page_num"]
    all_num=request.session["search"]["all_page_num"]
    if num+1 <= all_num:
        request.session["search"]["page_num"] = num + 1
    return redirect("sfa:index")


# ページネーション（最後）
def sfa_page_last(request):
    all_num=request.session["search"]["all_page_num"]
    request.session["search"]["page_num"]=all_num
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
    if parent_id=="":
        alert=Sfa_action.objects.filter(mitsu_id=mitsu_id,type=4,alert_check=0,day__lte=today)
    else:
        alert=Sfa_action.objects.filter(mitsu_id=parent_id,type=4,alert_check=0,day__lte=today)
        
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


# モーダル上部（確度、ステータス、備考）
def modal_top(request):
    mitsu_id=request.POST.get("mitsu_id")
    kakudo=request.POST.get("kakudo")
    kakudo_day=request.POST.get("kakudo_day")
    status=request.POST.get("status")
    bikou=request.POST.get("bikou")
 
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.kakudo_day=kakudo_day
    ins.status=status
    ins.bikou=bikou
    d={"見積中":"未","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待","サンクス":"サ","":""}
    ins.s_status=d[status]
    if status in ["終了","キャンセル","失注","サンクス"] and ins.last_status==None:
        ins.last_status=datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        ins.last_status=None
    ins.save()

    # 同期区分の設定
    if Sfa_group.objects.filter(mitsu_id_parent=mitsu_id).count()>0:
        douki="parent"
        parent_id=mitsu_id
    elif Sfa_group.objects.filter(mitsu_id_child=mitsu_id).count()>0:
        douki="child"
        parent_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
    else:
        douki="self"
        parent_id=mitsu_id

    li=[]
    li.append(parent_id)
    if douki=="parent" or douki=="child":
        ins=Sfa_group.objects.filter(mitsu_id_parent=parent_id)
        for i in ins:
            li.append(i.mitsu_id_child)

    for i in li:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.bikou=bikou
        ins.save()

    d={}
    return JsonResponse(d)


# モーダル下部（電話、メール、メモ、来店、アラート）
def modal_bot(request):
    act_id=request.POST.get("act_id")
    mitsu_id=request.POST.get("mitsu_id")
    cus_id=request.POST.get("cus_id")
    day=request.POST.get("day")
    type=request.POST.get("type")
    tel_result=request.POST.get("tel_result")
    text=request.POST.get("text")


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

    # 同期区分の設定
    if Sfa_group.objects.filter(mitsu_id_parent=mitsu_id).count()>0:
        douki="parent"
        parent_id=mitsu_id
    elif Sfa_group.objects.filter(mitsu_id_child=mitsu_id).count()>0:
        douki="child"
        parent_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
    else:
        douki="self"
        parent_id=mitsu_id

    li=[]
    li.append(parent_id)
    if douki=="parent" or douki=="child":
        ins=Sfa_group.objects.filter(mitsu_id_parent=parent_id)
        for i in ins:
            li.append(i.mitsu_id_child)

    # sfa_action
    if act_id =="":
        if type=="1":
            Sfa_action.objects.create(mitsu_id=parent_id,cus_id=cus_id,day=day,type=type,tel_result=tel_result,text=text)
        else:
            Sfa_action.objects.create(mitsu_id=parent_id,cus_id=cus_id,day=day,type=type,text=text)
    else:
        ins=Sfa_action.objects.get(act_id=act_id)
        ins.type=type
        ins.day=day
        if type=="1":
            ins.tel_result=tel_result
        ins.text=text
        ins.save()

    # 最終TEL
    tel_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).count() 
    if tel_count > 0:
        act_tel=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=act_tel.day
            ins.s_tel=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            if act_tel.tel_result=="対応":
                ins.s_tel_result=1
            else:
                ins.s_tel_result=2
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=None
            ins.s_tel=None
            ins.s_tel_result=0
            ins.save()

    # 最終メール
    mail_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).count()
    if mail_count > 0:
        act_mail=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=act_mail.day
            ins.s_mail=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ")"
            ins.s_mail_result=1
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=None
            ins.s_mail=None
            ins.s_mail_result=0
            ins.save()

    # コメント
    memo=Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day")
    memo1=""
    memo2=""
    shurui={1:"TEL",2:"メール",3:"メモ",4:"アラート",5:"来店"}
    if memo.count()>0:
        for i in memo:
            if i.text!="":
                memo1+=i.text + "、"
            memo2+=i.day + " " + shurui[i.type] + " " + i.tel_result + " " + i.text + "\n"
    for i in li:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.s_memo1=memo1[:-1]
        ins.s_memo2=memo2
        ins.save()

    res=list(Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day").values())
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

    Sfa_action.objects.get(act_id=act_id).delete()

    # 同期区分の設定
    if Sfa_group.objects.filter(mitsu_id_parent=mitsu_id).count()>0:
        douki="parent"
        parent_id=mitsu_id
    elif Sfa_group.objects.filter(mitsu_id_child=mitsu_id).count()>0:
        douki="child"
        parent_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
    else:
        douki="self"
        parent_id=mitsu_id

    li=[]
    li.append(parent_id)
    if douki=="parent" or douki=="child":
        ins=Sfa_group.objects.filter(mitsu_id_parent=parent_id)
        for i in ins:
            li.append(i.mitsu_id_child)

    # 最終TEL
    tel_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).count() 
    if tel_count > 0:
        act_tel=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=act_tel.day
            ins.s_tel=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            if act_tel.tel_result=="対応":
                ins.s_tel_result=1
            else:
                ins.s_tel_result=2
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=None
            ins.s_tel=None
            ins.s_tel_result=0
            ins.save()

    # 最終メール
    mail_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).count()
    if mail_count > 0:
        act_mail=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=act_mail.day
            ins.s_mail=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ")"
            ins.s_mail_result=1
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=None
            ins.s_mail=None
            ins.s_mail_result=0
            ins.save()

    # コメント
    memo=Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day")
    memo1=""
    memo2=""
    shurui={1:"TEL",2:"メール",3:"メモ",4:"アラート",5:"来店"}
    if memo.count()>0:
        for i in memo:
            if i.text!="":
                memo1+=i.text + "、"
            memo2+=i.day + " " + shurui[i.type] + " " + i.tel_result + " " + i.text + "\n"
    for i in li:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.s_memo1=memo1[:-1]
        ins.s_memo2=memo2
        ins.save()

    res=list(Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day").values())
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
        parent_id=""
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

        
    # 同期区分の設定
    if Sfa_group.objects.filter(mitsu_id_parent=mitsu_id).count()>0:
        douki="parent"
        parent_id=mitsu_id
    elif Sfa_group.objects.filter(mitsu_id_child=mitsu_id).count()>0:
        douki="child"
        parent_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
    else:
        douki="self"
        parent_id=mitsu_id

    li=[]
    li.append(parent_id)
    if douki=="parent" or douki=="child":
        ins=Sfa_group.objects.filter(mitsu_id_parent=parent_id)
        for i in ins:
            li.append(i.mitsu_id_child)

    # 備考
    bikou=Sfa_data.objects.get(mitsu_id=parent_id).bikou
    for i in li:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.bikou=bikou
        ins.save()

    # 最終TEL
    tel_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).count() 
    if tel_count > 0:
        act_tel=Sfa_action.objects.filter(mitsu_id=parent_id,type=1).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=act_tel.day
            ins.s_tel=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            if act_tel.tel_result=="対応":
                ins.s_tel_result=1
            else:
                ins.s_tel_result=2
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.tel_last_day=None
            ins.s_tel=None
            ins.s_tel_result=0
            ins.save()

    # 最終メール
    mail_count=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).count()
    if mail_count > 0:
        act_mail=Sfa_action.objects.filter(mitsu_id=parent_id,type=2).latest("day")
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=act_mail.day
            ins.s_mail=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ")"
            ins.s_mail_result=1
            ins.save()
    else:
        for i in li:
            ins=Sfa_data.objects.get(mitsu_id=i)
            ins.mail_last_day=None
            ins.s_mail=None
            ins.s_mail_result=0
            ins.save()

    # コメント
    memo=Sfa_action.objects.filter(mitsu_id=parent_id).order_by("day")
    memo1=""
    memo2=""
    shurui={1:"TEL",2:"メール",3:"メモ",4:"アラート",5:"来店"}
    if memo.count()>0:
        for i in memo:
            if i.text!="":
                memo1+=i.text + "、"
            memo2+=i.day + " " + shurui[i.type] + " " + i.tel_result + " " + i.text + "\n"
    for i in li:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.s_memo1=memo1[:-1]
        ins.s_memo2=memo2
        ins.save()

    return JsonResponse(d)


# CRMボタン
def kokyaku_detail_api(request):
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    request.session["crm_act_type"]="0"
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

    # 操作者
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
    sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    print(sousa_time,sousa_busho,sousa_tantou,"■ 案件表示設定")

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
        try:
            writer.writerow(line)
        except:
            print(line)
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

    # 操作者
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
    sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    print(sousa_time,sousa_busho,sousa_tantou,"■ 非表示一覧")

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

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
        
    return render(request,"sfa/member.html",{"list":ins,"act_user":act_user})


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

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    return render(request,"sfa/member.html",{"ans":ans,"list":ins,"act_user":act_user})



# ユニバURL発行
def credit_url(request):
    if "search" not in request.session:
        request.session["search"]={}
    if "tantou" not in request.session["search"]:
        request.session["search"]["tantou"]=""

    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
        tantou="不明"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
        tantou=Member.objects.get(tantou_id=act_id).tantou
    
    # URL発行
    if request.method == "POST":
        money=request.POST.get("money")
        meta_list=request.POST.get("meta_list")
        meta_list=json.loads(meta_list)

        url="https://checkout.univapay.com/forms/674afc52-65e2-4687-b207-3ed7b4ae8b3e"\
        "?appId=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcHBfdG9rZW4iLCJpYXQiOjE2NzM0MDM1MjUsIm1lcmNoYW50X2lkIjo"\
        "iMTFlZDI3NTUtODhiMy1iODcyLWI0ZjAtZmYzMzgwNTZhMmYwIiwic3RvcmVfaWQiOiIxMWVkMjc1Ni0xZTc2LWNhNTItYjQyMC1lMzk5YTlmMW"\
        "MwOGQiLCJkb21haW5zIjpbInAxLWludGwuY29tIl0sIm1vZGUiOiJsaXZlIiwiY3JlYXRvcl9pZCI6IjExZWQyNzU1LTg4YjMtYjg3Mi1iNGYwL"\
        "WZmMzM4MDU2YTJmMCIsInZlcnNpb24iOjEsImp0aSI6IjExZWQ5MTU2LTQ2NDktMzBlNy1iMDE5LWE3MThjZmZhYTcxYSJ9.xTUuVDg3HLi5eGD"\
        "JvEwGw9b7IlXfF3e9hJbkmpx8BvY"\
        "&cvvAuthorize=true&amount=" + money + "&type=recurring"
        for i,h in enumerate(meta_list):
            if i ==0:
                url+="&%E8%A6%8B%E7%A9%8D%E7%95%AA%E5%8F%B7=" + h
            else:
                url+="&%E8%A6%8B%E7%A9%8D%E7%95%AA%E5%8F%B7" + str(i) + "=" + h

        s = pyshorteners.Shortener()
        s_url=s.tinyurl.short(url)

        # 履歴
        meta_data=",".join(meta_list)
        day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Credit_url.objects.create(day=day,tantou=tantou,meta_data=meta_data,money=money,url=s_url)

        d={"url":s_url}
        return JsonResponse(d)
    
    return render(request,"sfa/credit_url.html",{"act_user":act_user})


# 管理画面
def kanri_index(request):
    if "search" not in request.session:
        request.session["search"]={}
    if "tantou" not in request.session["search"]:
        request.session["search"]["tantou"]=""
    ins=Credit_url.objects.all().order_by("day").reverse()[:100]
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/kanri.html",{"list":ins,"act_user":act_user})




# 元DB取込
def csv_imp_page(request):
    return render(request,"sfa/csv_imp.html")


# CSVデータを取り込む用
def csv_imp(request):

    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)


    # Crm_actionへの入力
    h=0
    for i in csv_list:
        if h!=0:
            ins=Hangire.objects.get(mitsu_id=i[0])
            ins.order_kubun=i[1]
            ins.save()
        h+=1




    # # Customerへの入力
    # h=0
    # for i in csv_list:
    #     if h!=0:

    #         # 顧客
    #         url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + str(i[0])
    #         res2=requests.get(url2)
    #         res2=res2.json()

    #         tel_search=None
    #         if res2["tel"] != None:
    #             tel_search=res2["tel"].replace("-","")
    #         tel_mob_search=None
    #         if res2["mobilePhone"] != None:
    #             tel_mob_search=res2["mobilePhone"].replace("-","")

    #         try:
    #             con_last=Customer.objects.get(cus_id=res2["id"]).contact_last
    #             if con_last==None or res2["lastEstimatedAt"]>con_last:
    #                 contact_last=res2["lastEstimatedAt"]
    #             else:
    #                 contact_last=con_last
    #         except:
    #             contact_last=res2["lastEstimatedAt"]
            
    #         try:
    #             Customer.objects.update_or_create(
    #             cus_id=res2["id"],
    #             defaults={
    #                 "cus_id":res2["id"],
    #                 "cus_url":res2["customerMstPageUrl"],
    #                 "cus_touroku":res2["createdAt"],
    #                 "com":res2["corporateName"],
    #                 "com_busho":res2["departmentName"],
    #                 "sei":res2["nameLast"],
    #                 "mei":res2["nameFirst"],
    #                 "pref":res2["prefecture"],
    #                 "city":res2["city"],
    #                 "address_1":res2["address1"],
    #                 "address_2":res2["address2"],
    #                 "tel":res2["tel"],
    #                 "tel_search":tel_search,
    #                 "tel_mob":res2["mobilePhone"],
    #                 "tel_mob_search":tel_mob_search,
    #                 "mail":res2["contactEmail"],
    #                 "mitsu_all":res2["totalEstimations"],
    #                 "juchu_all":res2["totalReceivedOrders"],
    #                 "juchu_money":res2["totalReceivedOrdersPrice"],
    #                 "mitsu_last":res2["lastEstimatedAt"],
    #                 "mitsu_last_busho_id":res2["lastHandledDepartmentId"],
    #                 "mitsu_last_busho":res2["lastHandledDepartmentName"],
    #                 "mitsu_last_tantou_id":res2["lastHandledId"],
    #                 "mitsu_last_tantou":res2["lastHandledName"],
    #                 "juchu_last":res2["lastOrderReceivedDate"],
    #                 "contact_last":contact_last,
    #                 "taimen":res2["isVisited"],
    #                 }
    #             )
    #         except:
    #             print(i[0])

    #     h+=1

 

    # # Crm_actionへの入力
    # h=0
    # for i in csv_list:
    #     if h!=0:
    #         Crm_action.objects.create(
    #             cus_id=i[0],
    #             day="2024-09-19",
    #             type=8,
    #             text="2024年 学割キャンペーン",
    #             approach_id="19"
    #             )
    #     h+=1
        
    

    return render(request,"sfa/csv_imp.html",{"message":"取込が完了しました！"})



# 色々と個別で動かす用
def clear_session(request):
    # request.session.clear()

    ins=Crm_action.objects.filter(approach_id="22")
    for i in ins:
        i.text="半年版切れ　2024年4～5月分"
        i.save()
            
    print("完了しました！")
  
    return redirect("sfa:index")