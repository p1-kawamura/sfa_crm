from django.shortcuts import render,redirect
from .models import Approach,Approach_list,Hangire
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

    ses=request.session["apr_search"]
 
    # フィルター
    fil={}
    fil["approach_id"]=ses["apr_id"]
    if ses["apr_busho"] != "":
        fil["busho_apr_id"]=ses["apr_busho"]
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

    # 部署設定
    apr_id=ses["apr_id"]
    busho_now=list(Member.objects.all().values_list("busho_id","busho").order_by("busho_id").distinct())
    busho_up=busho_now.copy()
    busho_list=list(Approach.objects.filter(approach_id=apr_id).values_list("busho_id","busho_name").order_by("busho_id").distinct())
    for i in busho_list:
        for h in busho_now:
            if i[0]==h[0]:
                break
        else:
            busho_up.append((i[0],i[1]))

    # 担当設定
    busho_id=ses["apr_busho"]
    tantou_now=list(Member.objects.all().values_list("tantou_id","tantou").order_by("tantou_id").distinct())
    tantou_up=tantou_now.copy()
    if busho_id=="":
        tantou_list=list(Approach.objects.filter(approach_id=apr_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Approach.objects.filter(approach_id=apr_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Approach.objects.filter(approach_id=apr_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))

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
        "busho_up":busho_up,
        "tantou_up":tantou_up,
        "busho_now":busho_now,
        "tantou_now":tantou_now,
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "ses":ses,
    }
    return render(request,"apr/approach.html",params)


# アプローチリスト部署クリック_上部
def approach_busho_up(request):
    apr_id=request.session["apr_search"]["apr_id"]
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_up=list(Member.objects.all().values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        tantou_list=list(Approach.objects.filter(approach_id=apr_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Approach.objects.filter(approach_id=apr_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Approach.objects.filter(approach_id=apr_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    d={"tantou_up":tantou_up}
    return JsonResponse(d)


# アプローチリスト部署クリック_下部
def approach_busho_now(request):
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_now=list(Member.objects.all().values_list("tantou_id","tantou"))
    else:
        tantou_now=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou"))
    d={"tantou_now":tantou_now}
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
    if tel_day!="":
        ins.tel_result=tel_result
    ins.tel_tantou=tel_tantou
    ins.tel_text=tel_text
    ins.save()

    if tel_day != "":
        if tel_tantou !="":
            text=tel_text + "（" + tel_tantou + "）"
        else:
            text=tel_text
        Crm_action.objects.create(cus_id=cus_id, day=tel_day, type=4, text=text, tel_result=tel_result)
        # 最終コンタクト日
        if tel_result=="対応":
            ins=Customer.objects.get(cus_id=cus_id)
            if tel_day > ins.contact_last:
                ins.contact_last=tel_day
                ins.save()
    
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


# アプローチリスト_別担当へ転送
def approach_send(request):
    pk=request.POST.get("pk")
    tantou_id=request.POST.get("tantou_id")
    busho_id=request.POST.get("busho_id")
    ins=Approach.objects.get(pk=pk)
    ins.tantou_apr_id=tantou_id
    ins.busho_apr_id=busho_id
    ins.save()
    d={}
    return JsonResponse(d)


# アプローチリスト設定_一覧表示
def approach_list_index(request):
    ins=Approach_list.objects.all()
    return render(request,"apr/approach_list.html",{"list":ins})


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
            
            # Crm_action
            Crm_action.objects.create(cus_id=i[10],day=day,type=8,text=title,approach_id=approach_id)

            # Approach 
            if action=="1":
                # url
                url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[10] + "/receivedOrders/" + i[1] + "/" + i[2]
                res=requests.get(url)
                res=res.json()
                res=res["receivedOrder"]
                mitsu_url=res["estimationPageUrl"]

                Approach.objects.create(
                    approach_id=approach_id,
                    mitsu_id=i[0],
                    mitsu_num=i[1],
                    mitsu_ver=i[2],
                    mitsu_url=mitsu_url,
                    order_kubun=i[3],
                    juchu_day=i[4],
                    busho_id=i[8],
                    busho_apr_id=i[8],
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
                    pref=i[30],
                    money=i[20],
                    kakou=i[22],
                    factory=i[24],
                    gara=i[25],
                    kigen=i[27]
                )
        h+=1
    ins=Approach_list.objects.all()
    return render(request,"apr/approach_list.html",{"ans":"yes","list":ins})


# 版切れリストCSV取込
def hangire_csv_imp(request):
    data = io.TextIOWrapper(request.FILES['csv2'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    h=0
    for i in csv_list:
        if h!=0:
            # url
            url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[13] + "/receivedOrders/" + i[1] + "/" + i[2]
            res=requests.get(url)
            res=res.json()
            res=res["receivedOrder"]
            mitsu_url=res["estimationPageUrl"]

            Hangire.objects.create(
                mitsu_id=i[0],
                mitsu_num=i[1],
                mitsu_ver=i[2],
                mitsu_url=mitsu_url,
                juchu_day=i[3],
                busho_id=i[14],
                busho_apr_id=i[14],
                busho_name=i[15],
                tantou_id=i[4],
                tantou_apr_id=i[4],
                tantou_sei=i[5],
                tantou_mei=i[6],
                cus_id=i[13],
                cus_com=i[10],
                cus_sei=i[7],
                cus_mei=i[8],
                cus_mail=i[9],
                pref=i[16],
                money=i[11],
                kakou=i[12],
            )
        h+=1
    return render(request,"apr/approach_list.html",{"ans2":"yes"})


# 版切れリスト
def hangire_index(request):
    if "han_search" not in request.session:
        request.session["han_search"]={}
    if "han_busho" not in request.session["han_search"]:
        request.session["han_search"]["han_busho"]=""
    if "han_tantou" not in request.session["han_search"]:
        request.session["han_search"]["han_tantou"]=""
    if "han_pref" not in request.session["han_search"]:
        request.session["han_search"]["han_pref"]=""
    if "han_result" not in request.session["han_search"]:
        request.session["han_search"]["han_result"]=[]
    if "han_day_st" not in request.session["han_search"]:
        request.session["han_search"]["han_day_st"]=""
    if "han_day_ed" not in request.session["han_search"]:
        request.session["han_search"]["han_day_ed"]=""
    if "page_num" not in request.session["han_search"]:
        request.session["han_search"]["page_num"]=1
    if "all_page_num" not in request.session["han_search"]:
        request.session["han_search"]["all_page_num"]=""
    if "han_jun" not in request.session["han_search"]:
        request.session["han_search"]["han_jun"]="0"

    ses=request.session["han_search"]
 
    # フィルター
    fil={}
    if ses["han_busho"] != "":
        fil["busho_apr_id"]=ses["han_busho"]
    if ses["han_tantou"] != "":
        fil["tantou_apr_id"]=ses["han_tantou"]
    if ses["han_pref"] != "":
        fil["pref"]=ses["han_pref"]
    if ses["han_day_st"] != "":
        fil["juchu_day__gte"]=ses["han_day_st"]
    if ses["han_day_ed"] != "":
        fil["juchu_day__lte"]=ses["han_day_ed"]
    

    # 進捗を含めない個数
    ins=Hangire.objects.filter(**fil)
    apr_type_list={0:"",1:"TEL",2:"メール"}
    result_list=[["0","未対応"],["1","不在"],["2","受注"],["3","失注"],["4","不要"],["5","検討中"]]
    for i in result_list:
        i.append(ins.filter(result=i[0]).count())

    # 進捗を含む
    if len(ses["han_result"])!=0:
        fil["result__in"]=ses["han_result"]
    
    # 並び順
    if ses["han_jun"]=="0":
        ins=Hangire.objects.filter(**fil).order_by("juchu_day")
    else:
        ins=Hangire.objects.filter(**fil).order_by("juchu_day").reverse()
    
    result=ins.count()
    #全ページ数
    if result == 0:
        all_num = 1
    elif result % 100 == 0:
        all_num = result / 100
    else:
        all_num = result // 100 + 1
    all_num=int(all_num)
    request.session["han_search"]["all_page_num"]=all_num
    num=ses["page_num"]
    if all_num==1:
        num=1
        request.session["han_search"]["page_num"]=1
    ins=ins[(num-1)*100 : num*100]

    # 部署設定
    busho_now=list(Member.objects.all().values_list("busho_id","busho").order_by("busho_id").distinct())
    busho_up=busho_now.copy()
    busho_list=list(Hangire.objects.all().values_list("busho_id","busho_name").order_by("busho_id").distinct())
    for i in busho_list:
        for h in busho_now:
            if i[0]==h[0]:
                break
        else:
            busho_up.append((i[0],i[1]))

    # 担当設定
    busho_id=ses["han_busho"]
    tantou_now=list(Member.objects.all().values_list("tantou_id","tantou").order_by("tantou_id").distinct())
    tantou_up=tantou_now.copy()
    
    if busho_id=="":
        tantou_list=list(Hangire.objects.all().values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Hangire.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Hangire.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
                
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
        "busho_up":busho_up,
        "tantou_up":tantou_up,
        "busho_now":busho_now,
        "tantou_now":tantou_now,
        "apr_type_list":apr_type_list,
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "ses":ses,
        "num":num,
        "all_num":all_num,
    }

    return render(request,"apr/hangire.html",params)


# 版切れ部署クリック_上部
def hangire_busho_up(request):
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_up=list(Member.objects.all().values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        tantou_list=list(Hangire.objects.all().values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Hangire.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Hangire.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    d={"tantou_up":tantou_up}
    return JsonResponse(d)


# 版切れ部署クリック_下部
def hangire_busho_now(request):
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_now=list(Member.objects.all().values_list("tantou_id","tantou"))
    else:
        tantou_now=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou"))
    d={"tantou_now":tantou_now}
    return JsonResponse(d)


# 版切れリストの検索
def hangire_search(request):
    request.session["han_search"]["han_busho"]=request.POST["han_busho"]
    request.session["han_search"]["han_tantou"]=request.POST["han_tantou"]
    request.session["han_search"]["han_pref"]=request.POST["han_pref"]
    request.session["han_search"]["han_day_st"]=request.POST["han_day_st"]
    request.session["han_search"]["han_day_ed"]=request.POST["han_day_ed"]
    request.session["han_search"]["han_result"]=request.POST.getlist("han_result")
    request.session["han_search"]["han_jun"]=request.POST["han_jun"]
    request.session["han_search"]["page_num"]=1
    return redirect("apr:hangire_index")


# 版切れリスト入力画面表示
def hangire_click(request):
    pk=request.POST.get("pk")
    apr_result=request.POST.get("apr_result")
    apr_day=request.POST.get("apr_day")
    apr_tantou=request.POST.get("apr_tantou")
    apr_type=request.POST.get("apr_type")
    tel_result=request.POST.get("tel_result")
    apr_text=request.POST.get("apr_text")
    cus_id=request.POST.get("cus_id")
    result_list={"0":"", "1":"不在", "2":"受注", "3":"失注", "4":"不要","5":"検討中"}

    ins=Hangire.objects.get(pk=pk)
    ins.result=apr_result
    ins.apr_day=apr_day
    ins.apr_type=apr_type
    if apr_day!="":
        ins.apr_tel_result=tel_result
    ins.apr_tantou=apr_tantou
    ins.apr_text=apr_text
    ins.save()

    if apr_day != "":
        if apr_tantou !="":
            text="【版切れ対応】　" + apr_text + "（" + apr_tantou + "）"
        else:
            text="【版切れ対応】　" + apr_text

        if apr_type=="1":
            Crm_action.objects.create(cus_id=cus_id, day=apr_day, type=4, text=text, tel_result=tel_result)
        elif apr_type=="2":
            Crm_action.objects.create(cus_id=cus_id, day=apr_day, type=2, text=text)
            
        # 最終コンタクト日
        if (apr_type=="1" and tel_result=="対応") or apr_type=="2":
            ins=Customer.objects.get(cus_id=cus_id)
            if apr_day > ins.contact_last:
                ins.contact_last=apr_day
                ins.save()
    
    ses=request.session["han_search"]
    fil={}
    if ses["han_busho"] != "":
        fil["busho_id"]=ses["han_busho"]
    if ses["han_tantou"] != "":
        fil["tantou_id"]=ses["han_tantou"]
    if ses["han_pref"] != "":
        fil["pref"]=ses["han_pref"]

    ins=Hangire.objects.filter(**fil)
    result_count=[]
    for i in range(6):
        result_count.append(ins.filter(result=i).count())

    d={
        "pk":pk,
        "ans":apr_result,
        "apr_result":result_list[apr_result],
        "apr_day":apr_day,
        "apr_tantou":apr_tantou,
        "apr_type":apr_type,
        "tel_result":tel_result,
        "apr_text":apr_text,
        "result_count":result_count,
        }
    return JsonResponse(d)


# 版切れリスト_別担当へ転送
def hangire_send(request):
    pk=request.POST.get("pk")
    tantou_id=request.POST.get("tantou_id")
    busho_id=request.POST.get("busho_id")
    ins=Hangire.objects.get(pk=pk)
    ins.tantou_apr_id=tantou_id
    ins.busho_apr_id=busho_id
    ins.save()
    d={}
    return JsonResponse(d)


def han_list_page_prev(request):
    num=request.session["han_search"]["page_num"]
    if num-1 > 0:
        request.session["han_search"]["page_num"] = num - 1
    return redirect("apr:hangire_index")


def han_list_page_first(request):
    request.session["han_search"]["page_num"] = 1
    return redirect("apr:hangire_index")


def han_list_page_next(request):
    num=request.session["han_search"]["page_num"]
    all_num=request.session["han_search"]["all_page_num"]
    if num+1 <= all_num:
        request.session["han_search"]["page_num"] = num + 1
    return redirect("apr:hangire_index")


def han_list_page_last(request):
    all_num=request.session["han_search"]["all_page_num"]
    request.session["han_search"]["page_num"]=all_num
    return redirect("apr:hangire_index")