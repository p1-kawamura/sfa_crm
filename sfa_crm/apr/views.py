from django.shortcuts import render,redirect
from .models import Approach,Approach_list
from crm.models import Crm_action,Customer
from sfa.models import Member
import requests
from django.http import JsonResponse
from datetime import date
import json
import csv
import io
from django.http import HttpResponse
import urllib.parse
from django.db.models import Q
from django.db.models import Max



# アプローチリスト
def approach_index(request):
    if "apr_search" not in request.session:
        request.session["apr_search"]={}
    if "apr_id" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_id"]=""
    if "apr_busho" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_busho"]=""
    if "apr_tantou" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_tantou"]=""
    if "apr_pref" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_pref"]=""
    if "apr_result" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_result"]=[]
    if "apr_ins" not in request.session["apr_search"]:
        request.session["apr_search"]["apr_ins"]=""

    ses=request.session["apr_search"]
 
    # フィルター
    fil={}
    fil["approach_id"]=ses["apr_id"]
    if ses["apr_busho"] != "":
        fil["busho_id"]=ses["apr_busho"]
    if ses["apr_tantou"] != "":
        fil["tantou_apr_id"]=ses["apr_tantou"]
    if ses["apr_pref"] != "":
        fil["pref"]=ses["apr_pref"]
    
    # 進捗を含めない個数
    ins=Approach.objects.filter(**fil)
    result_list=[["0","未対応"],["1","すでに受注済み"],["2","限定デザイン等"],["3","問合せあり"],["4","見積中"],["5","架電後：検討する"],
             ["6","架電後：見積"],["7","架電後：受注"],["8","架電後：不在"],["9","追加なし"],["10","新追履歴あり"],["11","折り返しあり"],["12","不要"]]
    for i in result_list:
        i.append(ins.filter(result=i[0]).count())

    # 進捗を含む
    if len(ses["apr_result"])!=0:
        fil["result__in"]=ses["apr_result"]
    ins=Approach.objects.filter(**fil)

    busho_list=list(Approach.objects.filter(approach_id=ses["apr_id"]).values_list("busho_id","busho_name").order_by("busho_id").distinct())
    tantou_list=list(Approach.objects.filter(approach_id=ses["apr_id"]).values_list("busho_id","tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
    tantou_id_list=list(Approach.objects.filter(approach_id=ses["apr_id"]).values_list("tantou_id",flat=True))
    tantou_member=Member.objects.all()
    for i in tantou_member:
        if i.tantou_id not in tantou_id_list:
            tantou_list.append((i.busho_id,i.tantou_id,i.tantou,""))
    tantou_list=sorted(tantou_list)

    apr_list=Approach_list.objects.filter(action=1)

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={
        "cus_list":ins,
        "act_user":act_user,
        "result_list":result_list,
        "apr_list":apr_list,
        "busho_list":busho_list,
        "tantou_list":tantou_list,
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "ses":ses,
    }
    return render(request,"apr/approach.html",params)


# アプローチリストのタイトル選択
def approach_title(request):
    approach_id=request.POST.get("approach_id")
    busho_list=list(Approach.objects.filter(approach_id=approach_id).values_list("busho_id","busho_name").order_by("busho_id").distinct())
    tantou_list=list(Approach.objects.filter(approach_id=approach_id).values_list("busho_id","tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
    tantou_id_list=list(Approach.objects.filter(approach_id=approach_id).values_list("tantou_id",flat=True))
    tantou_member=Member.objects.all()
    for i in tantou_member:
        if i.tantou_id not in tantou_id_list:
            tantou_list.append((i.busho_id,i.tantou_id,i.tantou,""))
    tantou_list=sorted(tantou_list)
    d={"busho_list":busho_list,"tantou_list":tantou_list}
    return JsonResponse(d)


# アプローチリストの検索
def approach_search(request):
    request.session["apr_search"]["apr_id"]=request.POST["apr_id"]
    request.session["apr_search"]["apr_busho"]=request.POST["apr_busho"]
    request.session["apr_search"]["apr_tantou"]=request.POST["apr_tantou"]
    request.session["apr_search"]["apr_pref"]=request.POST["apr_pref"]
    request.session["apr_search"]["apr_result"]=request.POST.getlist("apr_result")
    return redirect("apr:approach_index")


# アプローチリスト入力画面表示
def approach_click(request):
    pk=request.POST.get("pk")
    apr_result=request.POST.get("apr_result")
    tel_day=request.POST.get("tel_day")
    tel_tantou=request.POST.get("tel_tantou")
    tel_result=request.POST.get("tel_result")
    tel_text=request.POST.get("tel_text")
    cus_id=request.POST.get("cus_id")
    result_list={"0":"", "1":"すでに受注済み", "2":"限定デザイン等", "3":"問合せあり", "4":"見積中", "5":"架電後：検討する",
             "6":"架電後：見積","7":"架電後：受注","8":"架電後：不在", "9":"追加なし", "10":"新追履歴あり", "11":"折り返しあり","12":"不要"}

    ins=Approach.objects.get(pk=pk)
    ins.result=apr_result
    ins.tel_day=tel_day
    ins.tel_result=tel_result
    ins.tel_tantou=tel_tantou
    ins.tel_text=tel_text
    ins.save()

    if tel_day != "":
        text=tel_text + "（" + tel_tantou + "）"
        Crm_action.objects.create(cus_id=cus_id, day=tel_day, type=4, text=text, tel_result=tel_result)
    
    ses=request.session["apr_search"]
    fil={}
    fil["approach_id"]=ses["apr_id"]
    if ses["apr_busho"] != "":
        fil["busho_id"]=ses["apr_busho"]
    if ses["apr_tantou"] != "":
        fil["tantou_id"]=ses["apr_tantou"]
    if ses["apr_pref"] != "":
        fil["pref"]=ses["apr_pref"]

    ins=Approach.objects.filter(**fil)
    result_count=[]
    for i in range(13):
        result_count.append(ins.filter(result=i).count())

    d={
        "pk":pk,
        "ans":apr_result,
        "apr_result":result_list[apr_result],
        "tel_day":tel_day,
        "tel_tantou":tel_tantou,
        "tel_text":tel_text,
        "result_count":result_count,
        }
    return JsonResponse(d)


# 別担当へ転送
def approach_send(request):
    pk=request.POST.get("pk")
    tantou_id=request.POST.get("tantou_id")
    ins=Approach.objects.get(pk=pk)
    ins.tantou_apr_id=tantou_id
    ins.save()
    d={}
    return JsonResponse(d)


# アプローチリスト設定_一覧表示
def approach_list_index(request):
    ins=Approach_list.objects.all()

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"apr/approach_list.html",{"list":ins,"act_user":act_user})


# アプローチリスト設定_追加
def approach_list_add(request):
    approach_id=request.POST["approach_id"]
    title=request.POST["title"]
    day=request.POST["day"]
    action=request.POST["act"]

    # CSV取込
    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    # Approach_list
    Approach_list.objects.create(approach_id=approach_id,title=title,day=day,action=action)

    h=0
    for i in csv_list:
        if h!=0:
            
            # url
            url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[10] + "/receivedOrders/" + i[1] + "/" + i[2]
            res=requests.get(url)
            res=res.json()
            res=res["receivedOrder"]
            mitsu_url=res["estimationPageUrl"]

            # 都道府県
            url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[10]
            res2=requests.get(url2)
            res2=res2.json()
            pref=res2["prefecture"]

            # approach本体             
            Approach.objects.create(
                approach_id=approach_id,
                mitsu_id=i[0],
                mitsu_num=i[1],
                mitsu_ver=i[2],
                mitsu_url=mitsu_url,
                order_kubun=i[3],
                juchu_day=i[4],
                busho_id=i[8],
                busho_name=i[9],
                tantou_id=i[5],
                tantou_apr_id=i[5],
                tantou_sei=i[6],
                tantou_mei=i[7],
                cus_id=i[10],
                cus_com=i[16],
                cus_busho=i[17],
                cus_sei=i[11],
                cus_mei=i[12],
                cus_tel=i[18],
                cus_mob=i[19],
                cus_mail=i[13],
                pref=pref,
                money=i[20],
                kakou=i[22],
                factory=i[24],
                gara=i[25],
                kigen=i[27]
            )

            # Crm_action
            Crm_action.objects.create(cus_id=i[10],day=day,type=8,text=title,approach_id=approach_id)

        h+=1
 
    return redirect("apr:approach_list_index")



def hangire_index(request):
    return render(request,"apr/hangire.html")