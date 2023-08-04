from django.shortcuts import render,redirect
from .models import Crm_action,Grip
from sfa.models import Member
import requests
from django.http import JsonResponse
from datetime import date



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
    order=res2["totalOrders"]
    res2=res2["receivedOrders"]

    est_list=[]
    i=0
    kensu=0
    price=0
    for est in res2:
        li=[]
        li.append(est["firstEstimationDate"])
        li.append("est")
        li.append(i)
        est_list.append(li)
        i+=1
        #res3の計算
        if est["estimationStatus"] in ["受注","発送完了","終了"]:
            kensu+=1
            price+=est["totalPrice"]

    res3={
        "order":order,
        "price":price,
        "kensu":kensu,
    }

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
    if grip>0:
        tantou=Grip.objects.get(cus_id=cus_id).tantou_id
        tantou_name=Member.objects.get(tantou_id=tantou).tantou
    else:
        tantou_name=""

    params={
        "res":res,
        "res_det":res_det,
        "res3":res3,
        "alert":dic,
        "grip":grip,
        "tantou":tantou_name
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


def grip_index(request):
    ins=Grip.objects.all()
    list=[]
    for i in ins:
        dic={}
        dic["cus_id"]=i.cus_id
        dic["com"]=i.com
        dic["cus_name"]=i.cus_name
        dic["pref"]=i.pref
        dic["mitsu_count"]=i.mitsu_count
        # アラート
        today=str(date.today())
        alert=Crm_action.objects.filter(cus_id=i.cus_id,type=6,alert_check=0,day__lte=today).count()
        dic["alert"]=alert
        list.append(dic)
    return render(request,"crm/grip.html",{"list":list})


def grip_add(request):
    cus_id=request.POST.get("cus_id")
    cus_name=request.POST.get("cus_name")
    com=request.POST.get("com")
    pref=request.POST.get("pref")
    mitsu=request.POST.get("mitsu")

    Grip.objects.create(
        cus_id=cus_id,
        com=com,
        cus_name=cus_name,
        pref=pref,
        mitsu_count=mitsu,
        tantou_id=8
        )
    d={}
    return JsonResponse(d)
    