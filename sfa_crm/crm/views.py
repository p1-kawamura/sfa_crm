from django.shortcuts import render,redirect
from .models import Crm_action,Customer
from sfa.models import Member,Sfa_data,Sfa_action,Sfa_group
from apr.models import Approach,Approach_list
import requests
from django.http import JsonResponse
from datetime import date
import datetime
import json
import csv
import io
from django.http import HttpResponse
import urllib.parse
from django.db.models import Q
from django.db.models import Max



def index(request):
    if "cus_id" not in request.session:
        request.session["cus_id"]=[]
    return render(request,"crm/index.html")


def kokyaku_api(request):
    cus_id=request.session["cus_id"]

    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id
    res=requests.get(url)
    res=res.json()

    url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id + "/receivedOrders"
    res2=requests.get(url2)
    res2=res2.json()
    res2=res2["receivedOrders"]

    # 最終コンタクト日
    res["mitsu_last"]=Customer.objects.get(cus_id=cus_id).contact_last

    # 見積とコメント 一覧順の計算
    est_list=[]
    i=0
    for est in res2:
        li=[]
        li.append(est["firstEstimationDate"])
        li.append("est")
        li.append(i)
        est_list.append(li)
        i+=1

    ins=Crm_action.objects.filter(cus_id=cus_id)
    if ins.count()==0:
        last_list=sorted(est_list)
    else:
        act_list=[]
        for ac in ins:
            li=[]
            li.append(ac.day)
            li.append("act")
            li.append(ac.act_id)
            act_list.append(li)

        list_all=[]
        for est in est_list:
            list_all.append(est)
        for act in act_list:
            list_all.append(act)
        last_list=sorted(list_all)

    #最終成型
    res_det=[]
    for li in last_list:
        dic={}
        if li[1]=="est":
            dic["kubun"]="est"
            dic["day"]=res2[li[2]]["firstEstimationDate"]
            dic["est_num"]=res2[li[2]]["estimationNumber"] + "-" + str(res2[li[2]]["estimationVersion"])
            dic["status"]=res2[li[2]]["estimationStatus"]
            dic["money"]=res2[li[2]]["totalPrice"]
            dic["cus_id"]=cus_id
            dic["busho"]=res2[li[2]]["handledDepartmentName"]
            dic["tantou"]=res2[li[2]]["handledByName"]
        else:
            for ac in ins:
                if ac.act_id==li[2]:
                    dic["kubun"]="act"
                    dic["day"]=ac.day
                    dic["type"]=ac.type
                    dic["tel_result"]=ac.tel_result
                    dic["text"]=ac.text
                    dic["act_id"]=ac.act_id
        res_det.append(dic)

    # 最終成型_並び替え
    if request.session["crm_sort"]=="0":
        res_det=sorted(res_det,key=lambda x: x["day"])
    else:
        res_det=sorted(res_det,key=lambda x: x["day"], reverse=True)

    # アラート
    today=str(date.today())
    alert=Crm_action.objects.filter(cus_id=cus_id,type=6,alert_check=0,day__lte=today)
    dic={}
    if alert.count()!=0:
        dic["show"]=1
        for i in alert:
            dic["text"]=i.text
            dic["alert_num"]=i.act_id

    # グリップ顧客
    grip=Customer.objects.filter(cus_id=cus_id).count()
    if grip > 0:
        grip_busho_id=Customer.objects.get(cus_id=cus_id).grip_busho_id
        grip_tantou_id=Customer.objects.get(cus_id=cus_id).grip_tantou_id
    else:
        grip_busho_id=""
        grip_tantou_id=""
        
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    # 操作者
    tantou_id=request.session["search"]["tantou"]
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
    sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    print(sousa_time,sousa_busho,sousa_tantou,"■ 顧客詳細")

    params={
        "res":res,
        "res_det":res_det,
        "alert":dic,
        "grip":grip,
        "grip_busho_id":grip_busho_id,
        "grip_tantou_id":grip_tantou_id,
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":Member.objects.filter(busho_id=grip_busho_id),
        "act_user":act_user,
        "crm_sort":request.session["crm_sort"],
    }
    return render(request,"crm/index.html",params)


def crm_sort(request):
    sort=request.POST.get("crm_sort")
    request.session["crm_sort"]=sort
    d={}
    return JsonResponse(d)


def alert_check(request):
    alert_num=request.POST.get("alert_num")
    ins=Crm_action.objects.get(act_id=alert_num)
    ins.alert_check=1
    ins.save()
    d={}
    return JsonResponse(d)


def list_click_est(request):
    est_num=request.POST.get("est_num")
    sp=est_num.split("-")

    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + sp[0]+ "/receivedOrders/" + sp[1] + "/" + sp[2]
    res=requests.get(url)
    res=res.json()
    if Sfa_data.objects.filter(mitsu_num=sp[1],mitsu_ver=sp[2]).count() > 0:
        mitsu_id=Sfa_data.objects.get(mitsu_num=sp[1],mitsu_ver=sp[2]).mitsu_id
        # 同期対応
        try:
            mitsu_id=Sfa_group.objects.get(mitsu_id_child=mitsu_id).mitsu_id_parent
        except:
            pass
        bikou=Sfa_data.objects.get(mitsu_id=mitsu_id).bikou
        detail=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
    else:
        bikou=""
        detail=""
    d={"res":res,"bikou":bikou,"detail":detail}
    return JsonResponse(d)


def list_click_act(request):
    act_id=request.POST.get("act_id")
    ins=Crm_action.objects.get(act_id=act_id)
    res={"type":ins.type,"day":ins.day,"text":ins.text,"tel_result":ins.tel_result}
    d={"res":res}
    return JsonResponse(d)


def list_add(request):
    act_id=request.POST["act_id"]
    cus_id=request.POST["act_cus_id"]
    type=request.POST["act_type"]
    tel_result=request.POST["act_tel"]
    day=request.POST["act_day"]
    text=request.POST["act_text"]
    request.session["cus_id"]=cus_id

    if act_id=="":
        if type=="4":
            Crm_action.objects.create(cus_id=cus_id,day=day,type=type,tel_result=tel_result,text=text)
        else:
            Crm_action.objects.create(cus_id=cus_id,day=day,type=type,text=text)
    else:
        ins=Crm_action.objects.get(act_id=act_id)
        ins.day=day
        ins.type=type
        ins.text=text
        if type=="4":
            ins.tel_result=tel_result
        else:
            ins.tel_result=""
        ins.save()

    # 最終コンタクト日
    if type in ["2","5","7"] or (type=="4" and tel_result=="対応"):
        cus=Customer.objects.get(cus_id=cus_id)
        contact=cus.contact_last
        if contact==None or contact<day:
            cus.contact_last = day
            cus.save()

    return redirect("crm:kokyaku_api")


def list_del(request):
    act_id=request.POST.get("act_id")
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    Crm_action.objects.get(act_id=int(act_id)).delete()
    d={}
    return JsonResponse(d)


# グリップ追加
def grip_add(request):
    cus_id=request.POST.get("cus_id")
    busho_id=request.POST.get("busho_id")
    tantou_id=request.POST.get("tantou_id")
    # DB書込
    ins=Customer.objects.get(cus_id=cus_id)
    ins.grip_busho_id=busho_id
    ins.grip_tantou_id=tantou_id
    ins.save()
    d={}
    return JsonResponse(d)


# 備考更新
def crm_bikou(request):
    cus_id=request.POST.get("cus_id")
    bikou=request.POST.get("bikou")
    data={"remark":bikou}
    data=json.dumps(data)
    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id + "/remark"
    requests.put(url,data=data)
    d={}
    return JsonResponse(d)


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
    ins=Customer.objects.filter(mw_busho_id=busho_id,mw=1).order_by("mw_tantou_id")

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"crm/mw_csv.html",{"busho":busho,"list":ins,"ans":ans,"act_user":act_user})


# メールワイズ_追加
def mw_add(request):
    mw_add_list=request.POST.get("mw_list")
    mw_add_list=json.loads(mw_add_list)
    busho_id=request.session["search"]["busho"]
    tantou_id=request.session["search"]["tantou"]
    for i in mw_add_list:
        ins=Customer.objects.get(cus_id=i)
        ins.mw=1
        ins.mw_busho_id=busho_id
        ins.mw_tantou_id=tantou_id
        ins.mw_tantou=Member.objects.get(tantou_id=tantou_id).tantou
        ins.save()
    d={}
    return JsonResponse(d)


# メールワイズ_削除ボタン
def mw_delete(request,pk):
    ins=Customer.objects.get(pk=pk)
    ins.mw=0
    ins.mw_busho_id=""
    ins.mw_tantou_id=""
    ins.mw_tantou=""
    ins.save()
    return redirect("crm:mw_page")


#メールワイズ_CSV準備
def mw_make(request):
    mw_list=request.POST.get("list")
    mw_list=json.loads(mw_list)
    request.session["crm_mw_list"]=mw_list
    d={}
    return JsonResponse(d)


# メールワイズ_DL
def mw_download(request):
    mw_list=request.session["crm_mw_list"]
    mw_csv=[]
    for i in mw_list:
        ins=Customer.objects.get(cus_id=i)
        a=[
            ins.com or "", #会社
            (ins.sei or "") + (ins.mei or ""), #氏名
            ins.mail or "" , #メールアドレス
            ins.mw_tantou,  #担当
            "グリップ" #区分
        ]
        mw_csv.append(a)
        ins.mw=0
        ins.mw_busho_id=""
        ins.mw_tantou_id=""
        ins.mw_tantou=""
        ins.save()
    filename=urllib.parse.quote("顧客メール用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response


# 顧客管理一覧
def cus_list_index(request):
    if "cus_search" not in request.session:
        request.session["cus_search"]={}
    if "cus_id" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_id"]=""
    if "com" not in request.session["cus_search"]:
        request.session["cus_search"]["com"]=""
    if "cus_sei" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_sei"]=""
    if "cus_mei" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_mei"]=""
    if "cus_tel" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_tel"]=""
    if "pref" not in request.session["cus_search"]:
        request.session["cus_search"]["pref"]=""
    if "cus_mail" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_mail"]=""
    if "busho" not in request.session["cus_search"]:
        request.session["cus_search"]["busho"]=""
    if "tantou" not in request.session["cus_search"]:
        request.session["cus_search"]["tantou"]=""
    if "cus_touroku_st" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_touroku_st"]=""
    if "cus_touroku_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["cus_touroku_ed"]=""
    if "last_mitsu_st" not in request.session["cus_search"]:
        request.session["cus_search"]["last_mitsu_st"]=""
    if "last_mitsu_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["last_mitsu_ed"]=""
    if "last_juchu_st" not in request.session["cus_search"]:
        request.session["cus_search"]["last_juchu_st"]=""
    if "last_juchu_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["last_juchu_ed"]=""
    if "last_contact_st" not in request.session["cus_search"]:
        request.session["cus_search"]["last_contact_st"]=""
    if "last_contact_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["last_contact_ed"]=""
    if "mitsu_all_st" not in request.session["cus_search"]:
        request.session["cus_search"]["mitsu_all_st"]=""
    if "mitsu_all_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["mitsu_all_ed"]=""
    if "juchu_all_st" not in request.session["cus_search"]:
        request.session["cus_search"]["juchu_all_st"]=""
    if "juchu_all_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["juchu_all_ed"]=""
    if "juchu_money_st" not in request.session["cus_search"]:
        request.session["cus_search"]["juchu_money_st"]=""
    if "juchu_money_ed" not in request.session["cus_search"]:
        request.session["cus_search"]["juchu_money_ed"]=""
    if "grip" not in request.session["cus_search"]:
        request.session["cus_search"]["grip"]=[]
    if "royal" not in request.session["cus_search"]:
        request.session["cus_search"]["royal"]=[]
    if "taimen" not in request.session["cus_search"]:
        request.session["cus_search"]["taimen"]=[]
    if "page_num" not in request.session["cus_search"]:
        request.session["cus_search"]["page_num"]=1
    if "all_page_num" not in request.session["cus_search"]:
        request.session["cus_search"]["all_page_num"]=""
    if "apr_list" not in request.session["cus_search"]:
        request.session["cus_search"]["apr_list"]=""

    ses=request.session["cus_search"]

    # フィルター
    fil={}
    if ses["cus_id"] != "":
        fil["cus_id"]=ses["cus_id"]
    if ses["com"] != "":
        fil["com__contains"]=ses["com"].strip()
    if ses["cus_sei"] != "":
        fil["sei__contains"]=ses["cus_sei"].strip()
    if ses["cus_mei"] != "":
        fil["mei__contains"]=ses["cus_mei"].strip()
    if ses["pref"] != "":
        fil["pref"]=ses["pref"]
    if ses["cus_mail"] != "":
        fil["mail"]=ses["cus_mail"]
    if ses["busho"] != "":
        fil["mitsu_last_busho_id"]=ses["busho"]
    if ses["tantou"] != "":
        fil["mitsu_last_tantou_id"]=ses["tantou"]

    if ses["cus_touroku_st"] != "":
        fil["cus_touroku__gte"]=ses["cus_touroku_st"]
    if ses["cus_touroku_ed"] != "":
        fil["cus_touroku__lte"]=ses["cus_touroku_ed"]
    if ses["last_mitsu_st"] != "":
        fil["mitsu_last__gte"]=ses["last_mitsu_st"]
    if ses["last_mitsu_ed"] != "":
        fil["mitsu_last__lte"]=ses["last_mitsu_ed"]
    if ses["last_juchu_st"] != "":
        fil["juchu_last__gte"]=ses["last_juchu_st"]
    if ses["last_juchu_ed"] != "":
        fil["juchu_last__lte"]=ses["last_juchu_ed"]
    if ses["last_contact_st"] != "":
        fil["contact_last__gte"]=ses["last_contact_st"]
    if ses["last_contact_ed"] != "":
        fil["contact_last__lte"]=ses["last_contact_ed"]
    if ses["mitsu_all_st"] != "":
        fil["mitsu_all__gte"]=ses["mitsu_all_st"]
    if ses["mitsu_all_ed"] != "":
        fil["mitsu_all__lte"]=ses["mitsu_all_ed"]
    if ses["juchu_all_st"] != "":
        fil["juchu_all__gte"]=ses["juchu_all_st"]
    if ses["juchu_all_ed"] != "":
        fil["juchu_all__lte"]=ses["juchu_all_ed"]
    if ses["juchu_money_st"] != "":
        fil["juchu_money__gte"]=ses["juchu_money_st"]
    if ses["juchu_money_ed"] != "":
        fil["juchu_money__lte"]=ses["juchu_money_ed"]
    if ses["taimen"]:
        fil["taimen"]=True
    if ses["grip"]:
        fil["grip_tantou_id__gte"]=0
    if ses["royal"]:
        fil["royal"]=1

    if ses["cus_tel"] != "":
        tel=ses["cus_tel"].strip().replace("-","")
        ins_tel=list(Customer.objects.filter(tel_search=tel).values_list("cus_id",flat=True))
        ins_mob=list(Customer.objects.filter(tel_mob_search=tel).values_list("cus_id",flat=True))
        list_tel_mob=set(ins_tel + ins_mob)
        fil["cus_id__in"]=list_tel_mob

    if ses["apr_list"] != "":
        ins_apr=list(Crm_action.objects.filter(type=8,approach_id=ses["apr_list"]).values_list("cus_id",flat=True))
        fil["cus_id__in"]=ins_apr

    items=Customer.objects.filter(**fil).order_by("cus_touroku").reverse()
    result=items.count()
    #全ページ数
    if result == 0:
        all_num = 1
    elif result % 100 == 0:
        all_num = result / 100
    else:
        all_num = result // 100 + 1
    all_num=int(all_num)
    request.session["cus_search"]["all_page_num"]=all_num
    num=ses["page_num"]
    if all_num==1:
        num=1
        request.session["cus_search"]["page_num"]=1
    items=items[(num-1)*100 : num*100]

    member_list=Member.objects.all()

    # 部署、担当
    busho_list=list(Customer.objects.filter(mitsu_last_busho__isnull=False).\
                    values_list("mitsu_last_busho_id","mitsu_last_busho").order_by("mitsu_last_busho_id").distinct())
    if ses["busho"]!="":
        tantou_list=list(Customer.objects.filter(mitsu_last_busho_id=ses["busho"]).\
                         values_list("mitsu_last_tantou_id","mitsu_last_tantou").order_by("mitsu_last_tantou_id").distinct())
    else:
        tantou_list=list(Customer.objects.filter(mitsu_last_tantou__isnull=False).\
                         values_list("mitsu_last_tantou_id","mitsu_last_tantou").order_by("mitsu_last_tantou_id").distinct())

    # アプローチリスト
    apr_list={}
    for i in Approach_list.objects.all():
        if i.approach_id != "12":
            apr_list[str(i.approach_id)]=i.title

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    # 操作者
    tantou_id=request.session["search"]["tantou"]
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
    sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    print(sousa_time,sousa_busho,sousa_tantou,"■ 顧客検索")

    params={
        "cus_list":items,
        "member_list":member_list,
        "busho_list":busho_list,
        "tantou_list":tantou_list,
        "ses":ses,
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "apr_list":apr_list,
        "num":num,
        "all_num":all_num,
        "act_user":act_user,
        "result":result,
    }
    
    return render(request,"crm/cus_list.html",params)


# 顧客一覧の部署選択
def cus_list_busho(request):
    busho_id=request.POST.get("busho_id")
    if busho_id != "":
        tantou_list=list(Customer.objects.filter(mitsu_last_busho_id=busho_id).\
                         values_list("mitsu_last_tantou_id","mitsu_last_tantou").order_by("mitsu_last_tantou_id").distinct())
    else:
        tantou_list=list(Customer.objects.filter(mitsu_last_tantou__isnull=False).\
                         values_list("mitsu_last_tantou_id","mitsu_last_tantou").order_by("mitsu_last_tantou_id").distinct())
    d={"tantou_list":tantou_list}
    return JsonResponse(d)


# 顧客一覧の検索
def cus_list_search(request):
    request.session["cus_search"]["cus_id"]=request.POST["cus_id"]
    request.session["cus_search"]["com"]=request.POST["com"]
    request.session["cus_search"]["cus_sei"]=request.POST["cus_sei"]
    request.session["cus_search"]["cus_mei"]=request.POST["cus_mei"]
    request.session["cus_search"]["cus_tel"]=request.POST["cus_tel"]
    request.session["cus_search"]["pref"]=request.POST["pref"]
    request.session["cus_search"]["cus_mail"]=request.POST["cus_mail"]
    request.session["cus_search"]["busho"]=request.POST["busho"]
    request.session["cus_search"]["tantou"]=request.POST["tantou"]
    request.session["cus_search"]["cus_touroku_st"]=request.POST["cus_touroku_st"]
    request.session["cus_search"]["cus_touroku_ed"]=request.POST["cus_touroku_ed"]
    request.session["cus_search"]["last_mitsu_st"]=request.POST["last_mitsu_st"]
    request.session["cus_search"]["last_mitsu_ed"]=request.POST["last_mitsu_ed"]
    request.session["cus_search"]["last_juchu_st"]=request.POST["last_juchu_st"]
    request.session["cus_search"]["last_juchu_ed"]=request.POST["last_juchu_ed"]
    request.session["cus_search"]["last_contact_st"]=request.POST["last_contact_st"]
    request.session["cus_search"]["last_contact_ed"]=request.POST["last_contact_ed"]
    request.session["cus_search"]["mitsu_all_st"]=request.POST["mitsu_all_st"]
    request.session["cus_search"]["mitsu_all_ed"]=request.POST["mitsu_all_ed"]
    request.session["cus_search"]["juchu_all_st"]=request.POST["juchu_all_st"]
    request.session["cus_search"]["juchu_all_ed"]=request.POST["juchu_all_ed"]
    request.session["cus_search"]["juchu_money_st"]=request.POST["juchu_money_st"]
    request.session["cus_search"]["juchu_money_ed"]=request.POST["juchu_money_ed"]
    request.session["cus_search"]["grip"]=request.POST.getlist("grip")
    request.session["cus_search"]["royal"]=request.POST.getlist("royal")
    request.session["cus_search"]["taimen"]=request.POST.getlist("taimen")
    request.session["cus_search"]["apr_list"]=request.POST["apr_list"]
    request.session["cus_search"]["page_num"]=1

    return redirect("crm:cus_list_index")


def cus_list_page_prev(request):
    num=request.session["cus_search"]["page_num"]
    if num-1 > 0:
        request.session["cus_search"]["page_num"] = num - 1
    return redirect("crm:cus_list_index")


def cus_list_page_first(request):
    request.session["cus_search"]["page_num"] = 1
    return redirect("crm:cus_list_index")


def cus_list_page_next(request):
    num=request.session["cus_search"]["page_num"]
    all_num=request.session["cus_search"]["all_page_num"]
    if num+1 <= all_num:
        request.session["cus_search"]["page_num"] = num + 1
    return redirect("crm:cus_list_index")


def cus_list_page_last(request):
    all_num=request.session["cus_search"]["all_page_num"]
    request.session["cus_search"]["page_num"]=all_num
    return redirect("crm:cus_list_index")

