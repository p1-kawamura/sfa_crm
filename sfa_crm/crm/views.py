from django.shortcuts import render,redirect
from .models import Crm_action,Customer,Cus_group
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
from django.db.models import Sum,Max



def index(request):
    if "cus_id" not in request.session:
        request.session["cus_id"]=[]
    if "crm_act_type" not in request.session:
        request.session["crm_act_type"]="0"
    return render(request,"crm/index.html")


def kokyaku_api(request):
    cus_id=request.session["cus_id"]
    crm_act_type=request.session["crm_act_type"]

    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id
    res=requests.get(url)
    res=res.json()

    # 最終コンタクト日
    res["mitsu_last"]=Customer.objects.get(cus_id=cus_id).contact_last

    # グループ_自分の状態
    if Cus_group.objects.filter(cus_id_parent=cus_id).count()>0:
        kubun="parent"
        p_id=cus_id
    elif Cus_group.objects.filter(cus_id_child=cus_id).count()>0:
        kubun="child"
        p_id=Cus_group.objects.get(cus_id_child=cus_id).cus_id_parent
    else:
        kubun="self"

    # 親、子それぞれ
    ins_parent=""
    ins_child=""
    c_list=[]
    if kubun != "self":
        ins_parent=Customer.objects.get(cus_id=p_id)
        c_list=list(Cus_group.objects.filter(cus_id_parent=p_id).values_list("cus_id_child",flat=True))
        ins_child=Customer.objects.filter(cus_id__in=c_list)

    # グループ全体のメンバー
    if kubun == "self":
        a_list=[cus_id]
    else:
        a_list=set([cus_id,p_id] + c_list)
    
    # グループ_候補
    g_com=Customer.objects.get(cus_id=cus_id).com
    g_mail=Customer.objects.get(cus_id=cus_id).mail
    g_tel=Customer.objects.get(cus_id=cus_id).tel_search
    g_mob=Customer.objects.get(cus_id=cus_id).tel_mob_search

    ins_com=[]
    ins_mail=[]
    ins_tel=[]
    ins_mob=[]
    if g_com != None and g_com != "":
        ins_com=list(Customer.objects.filter(com__contains=g_com).values_list("cus_id",flat=True))
    if g_mail != None and g_mail != "":
        ins_mail=list(Customer.objects.filter(mail=g_mail).values_list("cus_id",flat=True))
    if g_tel != None and g_tel != "":
        ins_tel=list(Customer.objects.filter(tel_search=g_tel).values_list("cus_id",flat=True))
    if g_mob != None and g_mob != "":
        ins_mob=list(Customer.objects.filter(tel_mob_search=g_mob).values_list("cus_id",flat=True))

    ins_list=list(set(ins_tel + ins_mob + ins_mail + ins_com))
    group_list=[]
    for i in ins_list:
        if i != cus_id:
            g_dic={}
            ins=Customer.objects.get(cus_id=i)
            g_dic["id"]=ins.cus_id
            g_dic["com"]=ins.com
            g_dic["busho"]=ins.com_busho
            g_dic["sei"]=ins.sei
            g_dic["mei"]=ins.mei
            if Cus_group.objects.filter(cus_id_parent=i).count()>0 or Cus_group.objects.filter(cus_id_child=i).count()>0:
                g_dic["type"]="1"
            group_list.append(g_dic)


    # 見積とコメント 一覧順の計算
    if crm_act_type=="0":
        c_list=[cus_id]
    else:
        if kubun=="parent":
            c_list.append(cus_id)
        elif kubun=="child":
            c_list.append(p_id)

    res_det=[]
    for i in c_list:
        url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + str(i) + "/receivedOrders"
        res2=requests.get(url2)
        res2=res2.json()
        res2=res2["receivedOrders"]
        # 見積
        for h in res2:
            dic={}
            dic["kubun"]="est"
            dic["day"]=h["firstEstimationDate"]
            dic["est_num"]=h["estimationNumber"] + "-" + str(h["estimationVersion"])
            dic["status"]=h["estimationStatus"]
            dic["money"]=h["totalPrice"]
            dic["cus_id"]=i
            dic["busho"]=h["handledDepartmentName"]
            dic["tantou"]=h["handledByName"]
            res_det.append(dic)
        # コメント
        ins=Crm_action.objects.filter(cus_id=i)
        for h in ins:
            dic={}
            dic["kubun"]="act"
            dic["day"]=h.day
            dic["type"]=h.type
            dic["tel_result"]=h.tel_result
            dic["text"]=h.text
            dic["act_id"]=h.act_id
            res_det.append(dic)

    # 金額、件数など
    juchu_money=Customer.objects.filter(cus_id__in=a_list).aggregate(Sum("juchu_money"))["juchu_money__sum"]
    juchu_all=Customer.objects.filter(cus_id__in=a_list).aggregate(Sum("juchu_all"))["juchu_all__sum"]
    mitsu_all=Customer.objects.filter(cus_id__in=a_list).aggregate(Sum("mitsu_all"))["mitsu_all__sum"]
    try:
        mitsu_last=Customer.objects.filter(cus_id__in=a_list).aggregate(Max("mitsu_last"))["mitsu_last__max"]
    except:
        mitsu_last=""
    try:
        juchu_last=Customer.objects.filter(cus_id__in=a_list).aggregate(Max("juchu_last"))["juchu_last__max"]
    except:
        juchu_last=""
    try:
        contact_last=Customer.objects.filter(cus_id__in=a_list).aggregate(Max("contact_last"))["contact_last__max"]
    except:
        contact_last=""

    cus_data={}
    cus_data["juchu_money"]=juchu_money
    cus_data["juchu_all"]=juchu_all
    cus_data["mitsu_all"]=mitsu_all
    cus_data["mitsu_last"]=mitsu_last
    cus_data["juchu_last"]=juchu_last
    cus_data["contact_last"]=contact_last

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
    try:
        sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
        sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    except:
        sousa_busho=""
        sousa_tantou="不明"
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
        "crm_act_type":crm_act_type,
        "cus_id":cus_id,
        "kubun":kubun,
        "ins_parent":ins_parent,
        "ins_child":ins_child,
        "group_list":group_list,
        "cus_data":cus_data,
    }
    return render(request,"crm/index.html",params)


# 時系列表示順
def crm_sort(request):
    sort=request.POST.get("crm_sort")
    cus_id=request.POST.get("cus_id")
    request.session["crm_sort"]=sort
    request.session["cus_id"]=cus_id
    d={}
    return JsonResponse(d)


# 時系列表示タイプ
def crm_group_act(request):
    self_group=request.POST.get("self_group").replace("self_group_","")
    cus_id=request.POST.get("cus_id")
    request.session["crm_act_type"]=self_group
    request.session["cus_id"]=cus_id
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


# グループ編集ページ
def group_index(request):

    post_kubun=request.POST.get("post_kubun")
    cus_id=request.POST.get("cus_id")

    if post_kubun == "A": #顧客詳細から飛んできた
        com=Customer.objects.get(cus_id=cus_id).com
        mail=Customer.objects.get(cus_id=cus_id).mail
        tel=Customer.objects.get(cus_id=cus_id).tel_search
        mob=Customer.objects.get(cus_id=cus_id).tel_mob_search

        ins_com=[]
        ins_mail=[]
        ins_tel=[]
        ins_mob=[]
        if com != None and com != "":
            ins_com=list(Customer.objects.filter(com__contains=com).values_list("cus_id",flat=True))
        if mail != None and mail != "":
            ins_mail=list(Customer.objects.filter(mail=mail).values_list("cus_id",flat=True))
        if tel != None and tel != "":
            ins_tel=list(Customer.objects.filter(tel_search=tel).values_list("cus_id",flat=True))
        if mob != None and mob != "":
            ins_mob=list(Customer.objects.filter(tel_mob_search=mob).values_list("cus_id",flat=True))

        ins_list=list(set(ins_tel + ins_mob + ins_mail + ins_com))
        com=""; mail=""; tel=""

    else: #顧客設定の検索ボタンから
        com=request.POST.get("group_com")
        tel=request.POST.get("group_tel")
        mail=request.POST.get("group_mail")
        fil={}
        if com != "":
            fil["com__contains"]=com
        if mail != "":
            fil["mail"]=mail
        if tel != "":
            tel=tel.strip().replace("-","")
            ins_tel=list(Customer.objects.filter(tel_search=tel).values_list("cus_id",flat=True))
            ins_mob=list(Customer.objects.filter(tel_mob_search=tel).values_list("cus_id",flat=True))
            list_tel_mob=set(ins_tel + ins_mob)
            fil["cus_id__in"]=list_tel_mob

        if len(fil)>0:
            ins_list=list(Customer.objects.filter(**fil).values_list("cus_id",flat=True)) 
        else:
            ins_list=[]

    # 候補リスト
    ins_list=list(map(int,ins_list))
    ins_list.sort()
    cus_list=[]
    if len(ins_list)>0:
        for i in ins_list:
            dic={}
            url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + str(i)
            res=requests.get(url)
            res=res.json()
            dic["cus_id"]=str(res["id"])
            dic["cus_url"]=res["customerMstPageUrl"]
            dic["com"]=res["corporateName"]
            dic["busho"]=res["departmentName"]

            na=""
            if res["nameLast"]!=None:
                na=res["nameLast"]
            if res["nameFirst"]!=None:
                na+=res["nameFirst"]
            dic["name"]=na

            ad=""
            if res["prefecture"]!=None:
                ad+=res["prefecture"]
            if res["city"]!=None:
                ad+=res["city"]
            if res["address1"]!=None:
                ad+=res["address1"]
            if res["address2"]!=None:
                ad+=res["address2"]
            dic["adress"]=ad

            if Cus_group.objects.filter(cus_id_parent=i).count()>0:
                dic["kubun"]="parent"
            elif Cus_group.objects.filter(cus_id_child=i).count()>0:
                dic["kubun"]="child"
            else:
                dic["kubun"]="self"

            cus_list.append(dic)

    # 自分の状態
    if Cus_group.objects.filter(cus_id_parent=cus_id).count()>0:
        kubun="parent"
        p_id=cus_id
    elif Cus_group.objects.filter(cus_id_child=cus_id).count()>0:
        kubun="child"
        p_id=Cus_group.objects.get(cus_id_child=cus_id).cus_id_parent
    else:
        kubun="self"

    ins_self=Customer.objects.get(cus_id=cus_id)
    ins_parent=""
    ins_child=""
    ins_child_count=0
    if kubun != "self":
        ins_parent=Customer.objects.get(cus_id=p_id)
        c_list=list(Cus_group.objects.filter(cus_id_parent=p_id).values_list("cus_id_child",flat=True))
        ins_child=Customer.objects.filter(cus_id__in=c_list)
        ins_child_count=ins_child.count()

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={
        "cus_list":cus_list,
        "cus_id":cus_id,
        "com":com,
        "mail":mail,
        "tel":tel,
        "kubun":kubun,
        "ins_self":ins_self,
        "ins_parent":ins_parent,
        "ins_child":ins_child,
        "ins_child_count":ins_child_count,
        "act_user":act_user,
    }
    return render(request,"crm/group.html",params)


# グループ_削除
def group_del_all(request):
    parent_id=request.POST.get("parent_id").replace("顧客ID：","")
    ins=Cus_group.objects.filter(cus_id_parent=parent_id)
    for i in ins:
        i.delete()
    d={}
    return JsonResponse(d)


# グループ_子設定_追加
def group_add_child(request):
    parent_id=request.POST.get("parent_id").replace("顧客ID：","")
    chi_add_list=request.POST.get("chi_list")
    chi_add_list=json.loads(chi_add_list)
    for i in chi_add_list:
        chi_id=i.replace("check_","")
        Cus_group.objects.create(cus_id_parent=parent_id,cus_id_child=chi_id)
    d={}
    return JsonResponse(d)


# グループ_子設定_解除
def group_del_child(request):
    child_id=request.POST.get("child_id").replace("child_del_","")
    Cus_group.objects.get(cus_id_child=child_id).delete()
    d={}
    return JsonResponse(d)


# グループ_親設定_追加
def group_add_parent(request):
    parent_id=request.POST.get("parent_id").replace("radio_","")
    try:
        parent_id=Cus_group.objects.get(cus_id_child=parent_id).cus_id_parent
    except:
        parent_id=parent_id
    self_id=request.POST.get("self_id").replace("顧客ID：","")
    Cus_group.objects.create(cus_id_parent=parent_id,cus_id_child=self_id)
    d={}
    return JsonResponse(d)


# グループ_顧客詳細に戻る
def group_cus_submit(request):
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    request.session["crm_act_type"]="0"
    return redirect("crm:kokyaku_api")


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
    try:
        sousa_busho=Member.objects.get(tantou_id=tantou_id).busho
        sousa_tantou=Member.objects.get(tantou_id=tantou_id).tantou
    except:
        sousa_busho=""
        sousa_tantou="不明"
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

