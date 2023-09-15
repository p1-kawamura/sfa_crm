from django.shortcuts import render,redirect
from .models import Crm_action,Grip,Customer
from sfa.models import Member
import requests
from django.http import JsonResponse
from datetime import date
import json
import csv
from django.http import HttpResponse
import urllib.parse



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
        else:
            for ac in ins:
                if ac.act_id==li[2]:
                    dic["kubun"]="act"
                    dic["day"]=ac.day
                    dic["type"]=ac.type
                    dic["text"]=ac.text
                    dic["act_id"]=ac.act_id
        res_det.append(dic)

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
    grip=Grip.objects.filter(cus_id=cus_id).count()
    if grip > 0:
        busho_id=Grip.objects.get(cus_id=cus_id).busho_id
        tantou_id=Grip.objects.get(cus_id=cus_id).tantou_id
    else:
        busho_id=""
        tantou_id=""

    # メールワイズ、備考
    dic_bikou={"bikou1":"","bikou2":"","mw":0}
    if Customer.objects.filter(cus_id=cus_id).count() > 0:
        ins=Customer.objects.get(cus_id=cus_id)
        dic_bikou["bikou1"]=ins.bikou1
        dic_bikou["bikou2"]=ins.bikou2
        dic_bikou["mw"]=ins.mw
        
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={
        "res":res,
        "res_det":res_det,
        "alert":dic,
        "grip":grip,
        "busho_id":busho_id,
        "tantou_id":tantou_id,
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":Member.objects.filter(busho_id=busho_id),
        "dic_bikou":dic_bikou,
        "act_user":act_user,
    }
    return render(request,"crm/index.html",params)


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
    d={"res":res}
    return JsonResponse(d)


def list_click_act(request):
    act_id=request.POST.get("act_id")
    ins=Crm_action.objects.get(act_id=act_id)
    res={"type":ins.type,"day":ins.day,"text":ins.text}
    d={"res":res}
    return JsonResponse(d)


def list_add(request):
    act_id=request.POST["act_id"]
    cus_id=request.POST["act_cus_id"]
    type=request.POST["act_type"]
    day=request.POST["act_day"]
    text=request.POST["act_text"]
    request.session["cus_id"]=cus_id

    if act_id=="":
        Crm_action.objects.create(cus_id=cus_id,day=day,type=type,text=text)
    else:
        ins=Crm_action.objects.get(act_id=act_id)
        ins.day=day
        ins.type=type
        ins.text=text
        ins.save()
    return redirect("crm:kokyaku_api")


def list_del(request):
    act_id=request.POST.get("act_id")
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    Crm_action.objects.get(act_id=int(act_id)).delete()
    d={}
    return JsonResponse(d)


# グリップ一覧表示
def grip_index(request):
    tantou_id=request.session["search"]["tantou"]
    ins=Grip.objects.filter(tantou_id=tantou_id)
    list=[]
    for i in ins:
        url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i.cus_id
        res=requests.get(url)
        res=res.json()
        dic={}
        dic["cus_id"]=res["id"]
        dic["url"]=res["customerMstPageUrl"]
        dic["com"]=res["corporateName"]
        dic["cus_name"]=res["nameLast"] + res["nameFirst"]
        dic["pref"]=res["prefecture"]
        dic["mitsu_count"]=res["totalEstimations"]
        dic["juchu_count"]=res["totalReceivedOrders"]
        dic["juchu_money"]=res["totalReceivedOrdersPrice"]
        dic["juchu_last"]=res["lastOrderReceivedDate"]
        # アラート
        today=str(date.today())
        alert=Crm_action.objects.filter(cus_id=i.cus_id,type=6,alert_check=0,day__lte=today).count()
        dic["alert"]=alert
        list.append(dic)

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    return render(request,"crm/grip.html",{"list":list,"act_user":act_user})


# グリップ追加
def grip_add(request):
    cus_id=request.POST.get("cus_id")
    busho_id=request.POST.get("busho_id")
    tantou_id=request.POST.get("tantou_id")
    Grip.objects.update_or_create(
        cus_id=cus_id,
        defaults={
            "cus_id":cus_id,
            "busho_id":busho_id,
            "tantou_id":tantou_id,
            }
        )
    d={}
    return JsonResponse(d)


# メールワイズ作成チェックと備考
def mw_bikou(request):
    cus_id=request.POST.get("cus_id")
    bikou1=request.POST.get("bikou1")
    bikou2=request.POST.get("bikou2")
    mw=request.POST.get("mw")
    com=request.POST.get("com")
    cus_name=request.POST.get("cus_name")
    mail=request.POST.get("mail")
    busho_id=request.session["search"]["busho"]
    tantou_id=request.session["search"]["tantou"]
    tantou=Member.objects.get(tantou_id=tantou_id).tantou
    if mw=="true":
        mw=1
    else:
        mw=0
        busho_id=""
        tantou_id=""
        tantou=""
    Customer.objects.update_or_create(
        cus_id=cus_id,
        defaults={
            "cus_id":cus_id,
            "bikou1":bikou1,
            "bikou2":bikou2,
            "mw":mw,
            "busho_id":busho_id,
            "tantou_id":tantou_id,
            "tantou":tantou,
            "com":com,
            "name":cus_name,
            "mail":mail,
            }
        )
    d={}
    return JsonResponse(d)


# メールワイズ_表示ページ
def mw_page(request):
    busho_id=request.session["search"]["busho"]
    arr={"398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    busho=arr[busho_id]
    ins=Customer.objects.filter(busho_id=busho_id,mw=1).order_by("tantou_id")

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"crm/mw_csv.html",{"busho":busho,"list":ins,"act_user":act_user})


# メールワイズ_削除ボタン
def mw_delete(request,pk):
    ins=Customer.objects.get(pk=pk)
    ins.mw=0
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
            ins.com, #会社
            ins.name, #氏名
            ins.mail , #メールアドレス
            ins.tantou  #担当
        ]
        mw_csv.append(a)
        ins.mw=0
        ins.save()
    filename=urllib.parse.quote("【顧客】メールワイズ用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response
