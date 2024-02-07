from django.shortcuts import render,redirect
from .models import Crm_action,Customer
from sfa.models import Member,Sfa_data,Sfa_action,Sfa_group
import requests
from django.http import JsonResponse
from datetime import date
import json
import csv
from django.http import HttpResponse
import urllib.parse
from django.db.models import Q



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

    # 最終連絡日
    last=[]
    last_mitsu=[]
    for i in res2:
        last_mitsu.append(i["firstEstimationDate"])
    if len(last_mitsu)>0:
        last.append(max(last_mitsu))
        
    if Crm_action.objects.filter(cus_id=cus_id,type__in=[2,5,7]).count() > 0:
        last.append(Crm_action.objects.filter(cus_id=cus_id,type__in=[2,5,7]).latest("day").day)
    if Crm_action.objects.filter(cus_id=cus_id,type=4,tel_result="対応").count() > 0:
        last.append(Crm_action.objects.filter(cus_id=cus_id,type=4,tel_result="対応").latest("day").day)
    if Sfa_action.objects.filter(cus_id=cus_id,type=2).count() > 0:
        last.append(Sfa_action.objects.filter(cus_id=cus_id,type=2).latest("day").day)
    if Sfa_action.objects.filter(cus_id=cus_id,type=1,tel_result="対応").count() > 0:
        last.append(Sfa_action.objects.filter(cus_id=cus_id,type=1,tel_result="対応").latest("day").day)
    if len(last)>0:
        res["mitsu_last"]=max(last)

    # 見積とコメント計算
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
        busho_id=Customer.objects.get(cus_id=cus_id).grip_busho_id
        tantou_id=Customer.objects.get(cus_id=cus_id).grip_tantou_id
    else:
        busho_id=""
        tantou_id=""
        
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
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
    return redirect("crm:kokyaku_api")


def list_del(request):
    act_id=request.POST.get("act_id")
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    Crm_action.objects.get(act_id=int(act_id)).delete()
    d={}
    return JsonResponse(d)


# グリップAPI
def grip_index_api(request):
    tantou_id=request.session["search"]["tantou"]
    ins=Customer.objects.filter(grip_tantou_id=tantou_id)
    for i in ins:
        url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i.cus_id
        res=requests.get(url)
        res=res.json()
        
        # 最終コンタクト日
        url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i.cus_id + "/receivedOrders"
        res2=requests.get(url2)
        res2=res2.json()
        last=[]
        last_mitsu=[]
        for h in res2["receivedOrders"]:
            last_mitsu.append(h["firstEstimationDate"])
        if len(last_mitsu)>0:
            last.append(max(last_mitsu))
            mitsu_last=max(last_mitsu)
        else:
            mitsu_last=""

        if Crm_action.objects.filter(cus_id=res["id"],type__in=[2,5,7]).count() > 0:
            last.append(Crm_action.objects.filter(cus_id=res["id"],type__in=[2,5,7]).latest("day").day)
        if Crm_action.objects.filter(cus_id=res["id"],type=4,tel_result="対応").count() > 0:
            last.append(Crm_action.objects.filter(cus_id=res["id"],type=4,tel_result="対応").latest("day").day)
        if Sfa_action.objects.filter(cus_id=res["id"],type=2).count() > 0:
            last.append(Sfa_action.objects.filter(cus_id=res["id"],type=2).latest("day").day)
        if Sfa_action.objects.filter(cus_id=res["id"],type=1,tel_result="対応").count() > 0:
            last.append(Sfa_action.objects.filter(cus_id=res["id"],type=1,tel_result="対応").latest("day").day)
        
        if len(last)>0:
            contact_last=max(last)
        else:
            contact_last=""

        # DB書込
        i.cus_url=res["customerMstPageUrl"]
        i.com=res["corporateName"]
        i.com_busho=res["departmentName"]
        i.sei=res["nameLast"]
        i.mei=res["nameFirst"]
        i.pref=res["prefecture"]
        i.tel=res["tel"]
        i.tel_mob=res["mobilePhone"]
        i.mail=res["contactEmail"]
        i.mitsu_all=res["totalEstimations"]
        i.juchu_all=res["totalReceivedOrders"]
        i.juchu_money=res["totalReceivedOrdersPrice"]
        i.mitsu_last=mitsu_last
        i.juchu_last=res["lastOrderReceivedDate"]
        i.contact_last=contact_last
        i.save()

    return redirect("crm:grip_index")


# グリップ一覧表示
def grip_index(request):
    tantou_id=request.session["search"]["tantou"]
    ins=Customer.objects.filter(grip_tantou_id=tantou_id)
    grip_list=[]
    alert_all=0
    for i in ins:
        dic={}
        dic["cus_id"]=i.cus_id
        dic["url"]=i.cus_url
        dic["com"]=i.com
        dic["com_busho"]=i.com_busho
        dic["sei"]=i.sei
        dic["mei"]=i.mei
        dic["pref"]=i.pref
        dic["mitsu_all"]=i.mitsu_all
        dic["juchu_all"]=i.juchu_all
        dic["juchu_money"]=i.juchu_money
        dic["mitsu_last"]=i.mitsu_last
        dic["juchu_last"]=i.juchu_last
        dic["contact_last"]=i.contact_last

        # メールワイズ
        dic["mw"]=Customer.objects.get(cus_id=i.cus_id).mw

        # アラート
        today=str(date.today())
        alert=Crm_action.objects.filter(cus_id=i.cus_id,type=6,alert_check=0,day__lte=today).count()
        if alert>0:
            alert_all+=1
        dic["alert"]=alert

        # 案件発生
        est=Sfa_data.objects.filter(cus_id=i.cus_id,show=0).count()
        dic["est"]=est
        
        # 案件詳細
        est_detail=Sfa_data.objects.filter(cus_id=i.cus_id,show=0)
        if est_detail.count()>0:
            est_list=list(est_detail.values())
        else:
            est_list=""
        dic["est_list"]=est_list

        grip_list.append(dic)

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    return render(request,"crm/grip.html",{"list":grip_list,"act_user":act_user,"alert_all":alert_all})


# グリップ追加
def grip_add(request):
    cus_id=request.POST.get("cus_id")
    busho_id=request.POST.get("busho_id")
    tantou_id=request.POST.get("tantou_id")
    # 顧客情報
    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id
    res=requests.get(url)
    res=res.json()
    # 最終コンタクト日
    url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id + "/receivedOrders"
    res2=requests.get(url2)
    res2=res2.json()
    last=[]
    last_mitsu=[]
    for h in res2["receivedOrders"]:
        last_mitsu.append(h["firstEstimationDate"])
    if len(last_mitsu)>0:
        last.append(max(last_mitsu))
        mitsu_last=max(last_mitsu)
    else:
        mitsu_last=""

    if Crm_action.objects.filter(cus_id=res["id"],type__in=[2,5,7]).count() > 0:
        last.append(Crm_action.objects.filter(cus_id=res["id"],type__in=[2,5,7]).latest("day").day)
    if Crm_action.objects.filter(cus_id=res["id"],type=4,tel_result="対応").count() > 0:
        last.append(Crm_action.objects.filter(cus_id=res["id"],type=4,tel_result="対応").latest("day").day)
    if Sfa_action.objects.filter(cus_id=res["id"],type=2).count() > 0:
        last.append(Sfa_action.objects.filter(cus_id=res["id"],type=2).latest("day").day)
    if Sfa_action.objects.filter(cus_id=res["id"],type=1,tel_result="対応").count() > 0:
        last.append(Sfa_action.objects.filter(cus_id=res["id"],type=1,tel_result="対応").latest("day").day)
    
    if len(last)>0:
        contact_last=max(last)
    else:
        contact_last=""

    # DB書込
    ins=Customer.objects.get(cus_id=cus_id)
    ins.cus_url=res["customerMstPageUrl"]
    ins.com=res["corporateName"]
    ins.com_busho=res["departmentName"]
    ins.sei=res["nameLast"]
    ins.mei=res["nameFirst"]
    ins.pref=res["prefecture"]
    ins.tel=res["tel"]
    ins.tel_mob=res["mobilePhone"]
    ins.mail=res["contactEmail"]
    ins.mitsu_all=res["totalEstimations"]
    ins.juchu_all=res["totalReceivedOrders"]
    ins.juchu_money=res["totalReceivedOrdersPrice"]
    ins.mitsu_last=mitsu_last
    ins.juchu_last=res["lastOrderReceivedDate"]
    ins.contact_last=contact_last
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
    filename=urllib.parse.quote("グリップ顧客メール用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response
