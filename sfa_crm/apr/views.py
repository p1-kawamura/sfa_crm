from django.shortcuts import render,redirect
from .models import Approach_list,Hangire
from crm.models import Crm_action,Customer
from sfa.models import Member
import requests
from django.http import JsonResponse
from datetime import date
import csv
import io
from datetime import date
from django_pandas.io import read_frame
import pandas as pd



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
    day_type=request.POST["day_type"]

    # CSV取込
    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    # Approach_list
    Approach_list.objects.create(approach_id=approach_id,title=title,day=day,action=action,day_type=day_type)

    h=0
    for i in csv_list:
        if h!=0:
            
            # Crm_action
            Crm_action.objects.create(cus_id=i[10],day=day,type=8,text=title,approach_id=approach_id)

            # 見積
            url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[10] + "/receivedOrders/" + i[1] + "/" + i[2]
            res=requests.get(url)
            res=res.json()
            res=res["receivedOrder"]
            mitsu_url=res["estimationPageUrl"]

            #Customer
            url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[10]
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

            # Hangire（2024.10.03 アプローチリストを版切れに統合）
            Hangire.objects.create(
                approach_id=approach_id,
                mitsu_id=i[0],
                mitsu_num=i[1],
                mitsu_ver=i[2],
                mitsu_url=mitsu_url,
                juchu_day=i[4],
                order_kubun=i[3],
                busho_id=i[8],
                busho_name=i[9],
                busho_apr_id=i[8],
                busho_apr_name=i[9],
                tantou_id=i[5],
                tantou_sei=i[6],
                tantou_mei=i[7],
                tantou_apr_id=i[5],
                tantou_apr_name=i[6] + " " + i[7],
                cus_id=i[10],
                cus_url=res2["customerMstPageUrl"],
                cus_com=i[15],
                cus_sei=i[11],
                cus_mei=i[12],
                cus_tel=res2["tel"],
                cus_tel_search=tel_search,
                cus_mob=res2["mobilePhone"],
                cus_mob_search=tel_mob_search,
                cus_mail=i[13],
                pref=i[14],
                money=i[18],
                kakou=i[19],
                yobi_1=i[20],
                yobi_2=i[21],
                yobi_3=i[22],
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
            # 見積
            url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[13] + "/receivedOrders/" + i[1] + "/" + i[2]
            res=requests.get(url)
            res=res.json()
            res=res["receivedOrder"]
            mitsu_url=res["estimationPageUrl"]

            #Customer
            url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + i[13]
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

            Hangire.objects.create(
                mitsu_id=i[0],
                mitsu_num=i[1],
                mitsu_ver=i[2],
                mitsu_url=mitsu_url,
                juchu_day=i[3],
                order_kubun=i[17],
                busho_id=i[14],
                busho_name=i[15],
                busho_apr_id=i[14],
                busho_apr_name=i[15],
                tantou_id=i[4],
                tantou_sei=i[5],
                tantou_mei=i[6],
                tantou_apr_id=i[4],
                tantou_apr_name=i[5] + " " + i[6],
                cus_id=i[13],
                cus_url=res2["customerMstPageUrl"],
                cus_com=i[10],
                cus_sei=i[7],
                cus_mei=i[8],
                cus_tel=res2["tel"],
                cus_tel_search=tel_search,
                cus_mob=res2["mobilePhone"],
                cus_mob_search=tel_mob_search,
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
    if "han_com" not in request.session["han_search"]:
        request.session["han_search"]["han_com"]=""
    if "han_sei" not in request.session["han_search"]:
        request.session["han_search"]["han_sei"]=""
    if "han_mei" not in request.session["han_search"]:
        request.session["han_search"]["han_mei"]=""
    if "han_tel" not in request.session["han_search"]:
        request.session["han_search"]["han_tel"]=""
    if "han_mail" not in request.session["han_search"]:
        request.session["han_search"]["han_mail"]=""
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
    if "sort_name" not in request.session["han_search"]:
        request.session["han_search"]["sort_name"]="juchu_day"
    if "sort_jun" not in request.session["han_search"]:
        request.session["han_search"]["sort_jun"]="0"  
    if "han_modal_jun" not in request.session["han_search"]:
        request.session["han_search"]["han_modal_jun"]="1"
    if "han_pk" not in request.session["han_search"]:
        request.session["han_search"]["han_pk"]="0"
    if "han_or_apr" not in request.session["han_search"]:
        request.session["han_search"]["han_or_apr"]="han"
    if "approach_id" not in request.session["han_search"]:
        request.session["han_search"]["approach_id"]=""

    ses=request.session["han_search"]
 
    # フィルター
    fil={}
    if ses["han_or_apr"] == "han":
        fil["approach_id"]="0"
        approach_id="0"
    elif ses["han_or_apr"] == "apr":    
        fil["approach_id"]=ses["approach_id"]
        approach_id=ses["approach_id"]
    elif ses["han_or_apr"] == "nou":    
        fil["approach_id"]="N"
        approach_id="N"

    if ses["han_busho"] != "":
        fil["busho_apr_id"]=ses["han_busho"]
    if ses["han_tantou"] != "":
        fil["tantou_apr_id"]=ses["han_tantou"]
    if ses["han_pref"] != "":
        fil["pref"]=ses["han_pref"]
    if ses["han_com"] != "":
        fil["cus_com__contains"]=ses["han_com"].strip()
    if ses["han_sei"] != "":
        fil["cus_sei__contains"]=ses["han_sei"].strip()
    if ses["han_mei"] != "":
        fil["cus_mei__contains"]=ses["han_mei"].strip()
    if ses["han_mail"] != "":
        fil["cus_mail"]=ses["han_mail"]
    if ses["han_day_st"] != "":
        fil["juchu_day__gte"]=ses["han_day_st"]
    if ses["han_day_ed"] != "":
        fil["juchu_day__lte"]=ses["han_day_ed"]

    if ses["han_tel"] != "":
        tel=ses["han_tel"].strip().replace("-","")
        ins_tel=list(Hangire.objects.filter(cus_tel_search=tel).values_list("cus_id",flat=True))
        ins_mob=list(Hangire.objects.filter(cus_mob_search=tel).values_list("cus_id",flat=True))
        list_tel_mob=set(ins_tel + ins_mob)
        fil["cus_id__in"]=list_tel_mob
    

    # 進捗を含めない個数
    ins=Hangire.objects.filter(**fil)
    apr_type_list={0:"",4:"TEL",2:"メール",1:"メモ"}
    result_list=[["0","未対応"],["1","アプローチしない"],["tran","他の担当へ転送"],["2","不在"],["3","検討します"],
                 ["4","失注/予定なし"],["5","架電により案件化"],["6","受注"],["7","その他"]]
    for i in result_list:
        i.append(ins.filter(result=i[0]).count())

    # 進捗を含む
    if len(ses["han_result"])!=0:
        fil["result__in"]=ses["han_result"]
    
    # 並び順
    if ses["sort_jun"]=="0":
        ins=Hangire.objects.filter(**fil).order_by(ses["sort_name"])
    else:
        ins=Hangire.objects.filter(**fil).order_by(ses["sort_name"]).reverse()
    
    
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
    busho_list=list(Hangire.objects.filter(approach_id=approach_id).values_list("busho_id","busho_name").order_by("busho_id").distinct())
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
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))

    # その他必要情報
    modal_sort=request.session["han_search"]["han_modal_jun"]
    pk=request.session["han_search"]["han_pk"]
    apr_list=Approach_list.objects.filter(action=1)

    if ses["han_or_apr"] == "nou": 
        sort_list={"juchu_day":"発送完了日","money":"金額"}
    elif ses["han_or_apr"] == "apr" and ses["approach_id"]!="":
        if Approach_list.objects.get(approach_id=ses["approach_id"]).day_type == 1:
            sort_list={"juchu_day":"見積日","money":"金額"}
    else:
        sort_list={"juchu_day":"受注日","money":"金額"}
    
                
    # アクティブ担当
    try:
        act_id=request.session["search"]["tantou"]
    except:
        act_id=""
        
    if act_id=="":
        act_user="担当者が未設定です"
        modal_user=""
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
        modal_user=Member.objects.get(tantou_id=act_id).tantou.split(" ")[0]

    params={
        "cus_list":ins,
        "act_user":act_user,
        "modal_user":modal_user,
        "result_list":result_list,
        "apr_list":apr_list,
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
        "sort_list":sort_list,
        "ses":ses,
        "num":num,
        "all_num":all_num,
        "modal_sort":modal_sort,
        "pk":int(pk),
    }

    return render(request,"apr/hangire.html",params)


# 版切れ部署クリック_上部
def hangire_busho_up(request):
    busho_id=request.POST.get("busho_id")
    han_or_apr=request.session["han_search"]["han_or_apr"]
    approach_id=request.session["han_search"]["approach_id"]
    if han_or_apr=="han":
        approach_id="0"

    if busho_id=="":
        tantou_up=list(Member.objects.all().values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    elif busho_id not in ["398","400","401","402"]:
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=[]
        for i in tantou_list:
            tantou_up.append((i[0],i[1] + " " + i[2]))
    else:
        tantou_list=list(Hangire.objects.filter(approach_id=approach_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
        tantou_up=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou").order_by("tantou_id").distinct())
        for i in tantou_list:
            for h in tantou_up:
                if i[0]==h[0]:
                    break
            else:
                tantou_up.append((i[0],i[1] + " " + i[2]))
    d={"tantou_up":tantou_up}
    return JsonResponse(d)


# 対象リストを選択
def choice_id(request):
    han_or_apr=request.POST.get("han_or_apr")
    request.session["han_search"]["han_or_apr"]=han_or_apr
    if han_or_apr == "apr":
        request.session["han_search"]["approach_id"]=request.POST.get("approach_id")
    d={}
    return JsonResponse(d)


# 版切れリストの検索
def hangire_search(request):
    request.session["han_search"]["han_busho"]=request.POST["han_busho"]
    request.session["han_search"]["han_tantou"]=request.POST["han_tantou"]
    request.session["han_search"]["han_pref"]=request.POST["han_pref"]
    request.session["han_search"]["han_com"]=request.POST["han_com"]
    request.session["han_search"]["han_sei"]=request.POST["han_sei"]
    request.session["han_search"]["han_mei"]=request.POST["han_mei"]
    request.session["han_search"]["han_tel"]=request.POST["han_tel"]
    request.session["han_search"]["han_mail"]=request.POST["han_mail"]
    request.session["han_search"]["han_day_st"]=request.POST["han_day_st"]
    request.session["han_search"]["han_day_ed"]=request.POST["han_day_ed"]
    request.session["han_search"]["han_result"]=request.POST.getlist("han_result")
    request.session["han_search"]["sort_name"]=request.POST["sort_name"]
    request.session["han_search"]["sort_jun"]=request.POST["sort_jun"]
    request.session["han_search"]["page_num"]=1
    return redirect("apr:hangire_index")


# 版切れモーダル_TOP
def hangire_modal_show_top(request):
    pk=request.POST.get("pk").replace("open_","")
    request.session["han_search"]["han_pk"]=pk
    result=list(Hangire.objects.filter(pk=pk).values())
    d={"result":result}        
    return JsonResponse(d)


# 版切れモーダル_BOT
def hangire_modal_show_bot(request):
    pk=request.POST.get("pk").replace("open_","")
    cus_id=Hangire.objects.get(pk=pk).cus_id
    res_det=[]
    url2="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id + "/receivedOrders"
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
        dic["cus_id"]=cus_id
        dic["busho"]=h["handledDepartmentName"]
        dic["tantou"]=h["handledByName"]
        res_det.append(dic)
    # コメント
    ins=Crm_action.objects.filter(cus_id=cus_id)
    for h in ins:
        dic={}
        dic["kubun"]="act"
        dic["day"]=h.day
        dic["type"]=h.type
        dic["tel_result"]=h.tel_result
        dic["text"]=h.text
        dic["act_id"]=h.act_id
        res_det.append(dic)
    # 並び替え
    if request.session["han_search"]["han_modal_jun"]=="0":
        res_det=sorted(res_det,key=lambda x: x["day"])
    else:
        res_det=sorted(res_det,key=lambda x: x["day"], reverse=True)

    d={"cus_act":res_det}
    return JsonResponse(d)


# 版切れモーダル_表示順
def hangire_modal_sort(request):
    jun=request.POST.get("jun")
    request.session["han_search"]["han_modal_jun"]=jun
    d={}
    return JsonResponse(d)


# 版切れモーダル_リストクリック
def hangire_modal_list_click(request):
    act_id=request.POST.get("act_id")
    ins=Crm_action.objects.get(act_id=act_id)
    res={"type":ins.type,"tel":ins.tel_result,"day":ins.day,"text":ins.text}
    d={"res":res}
    return JsonResponse(d)


# 版切れモーダル_決定ボタン
def hangire_modal_btn(request):
    pk=request.POST.get("pk")
    act_id=request.POST.get("act_id")
    result=request.POST.get("result")
    tantou=request.POST.get("tantou")
    day=request.POST.get("day")
    type=request.POST.get("type")
    tel_result=request.POST.get("tel_result")
    text=request.POST.get("text")
    cus_id=Hangire.objects.get(pk=pk).cus_id

    d={}
    try:
        # Crm_actionへ
        text2=text + "（" + tantou + "）"
            
        if act_id=="" or act_id==None:
            if type=="4":
                Crm_action.objects.create(cus_id=cus_id,day=day,type=type,tel_result=tel_result,text=text2)
            else:
                Crm_action.objects.create(cus_id=cus_id,day=day,type=type,text=text2)

            # Hangireへ
            ins=Hangire.objects.get(pk=pk)
            ins.result=result
            ins.apr_day=day
            ins.apr_tantou=tantou
            ins.apr_type=type
            ins.apr_tel_result=tel_result
            ins.apr_text=text
            ins.save()

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
        if type=="2" or (type=="4" and tel_result=="対応"):
            try:
                cus=Customer.objects.get(cus_id=cus_id)
                contact=cus.contact_last
                if contact==None or contact<day:
                    cus.contact_last = day
                    cus.save()
            except:
                pass

        d["result"]="ok"

    except:
        d["result"]="no"
    
    return JsonResponse(d)


# 版切れモーダル_削除ボタン
def hangire_modal_del(request):
    act_id=request.POST.get("act_id")
    Crm_action.objects.get(act_id=act_id).delete()
    d={}
    return JsonResponse(d)


# 版切れモーダル_最終結果を削除
def hangire_modal_result_del(request):
    pk=request.POST.get("pk")
    ins=Hangire.objects.get(pk=pk)
    ins.result=0
    ins.apr_day=None
    ins.apr_tantou=None
    ins.apr_type=0
    ins.apr_tel_result=None
    ins.apr_text=None
    ins.save()
    d={}
    return JsonResponse(d)


# 版切れモーダル_結果を「受注」に変更
def hangire_modal_result_juchu(request):
    pk=request.POST.get("pk")
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        modal_user=""
    else:
        modal_user=Member.objects.get(tantou_id=act_id).tantou.split(" ")[0]
    # Hangire
    ins=Hangire.objects.get(pk=pk)
    ins.result=6
    ins.apr_day=date.today()
    ins.apr_tantou=modal_user
    ins.apr_type=1
    ins.apr_text="受注確認"
    ins.save()
    # Crm_action
    cus_id=Hangire.objects.get(pk=pk).cus_id
    Crm_action.objects.create(cus_id=cus_id,day=date.today(),type=1,text="受注確認（" + modal_user + "）")
    d={}
    return JsonResponse(d)


# 版切れモーダル_転送先部署クリック
def hangire_busho_now(request):
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_now=list(Member.objects.all().values_list("tantou_id","tantou"))
    else:
        tantou_now=list(Member.objects.filter(busho_id=busho_id).values_list("tantou_id","tantou"))
    d={"tantou_now":tantou_now}
    return JsonResponse(d)


# 版切れリスト_別担当へ転送
def hangire_modal_send(request):
    pk=request.POST.get("pk")
    busho_id=request.POST.get("busho_id")
    busho_name=request.POST.get("busho_name")
    tantou_id=request.POST.get("tantou_id")
    tantou_name=request.POST.get("tantou_name")

    ins=Hangire.objects.get(pk=pk)
    ins.busho_apr_id=busho_id
    ins.busho_apr_name=busho_name
    ins.tantou_apr_id=tantou_id
    ins.tantou_apr_name=tantou_name
    ins.save()
    d={}
    return JsonResponse(d)


# 版切れリスト_前回モーダル分カラークリア
def hangire_color_clear(request):
    request.session["han_search"]["han_pk"]="0"
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


# 集計ページ
def shukei_index(request):
    if "han_apr_shukei" not in request.session:
        request.session["han_apr_shukei"]={}
    if "shukei_id" not in request.session["han_apr_shukei"]:
        request.session["han_apr_shukei"]["shukei_id"]="0"
    if "shukei_month" not in request.session["han_apr_shukei"]:
        request.session["han_apr_shukei"]["shukei_month"]=""

    ses=request.session["han_apr_shukei"]
    fil={}
    fil["approach_id"]=ses["shukei_id"]
    if ses["shukei_month"] != "":
        fil["juchu_day__gte"]=ses["shukei_month"] + "-01"
        fil["juchu_day__lte"]=ses["shukei_month"] + "-31"
    
    # 除外する担当
    del_list=["812","811","810","809","54","53","51","394"]
    
    ins=Hangire.objects.filter(**fil).exclude(tantou_id__in=del_list)

    # アプローチの場合は部署名を変更（版切れはデータ量が多いのでそのまま）
    if ses["shukei_id"]=="0" or ses["shukei_id"]=="N":
        df=read_frame(ins)
    else:
        list_ch=[]
        for i in ins:
            change_busho_id=i.busho_apr_id
            if Member.objects.filter(tantou_id=i.tantou_apr_id).count() > 0:
                change_busho_id=Member.objects.get(tantou_id=i.tantou_apr_id).busho_id
            list_ch.append([change_busho_id,i.tantou_apr_id,i.tantou_apr_name,i.juchu_day,i.result])
        df=pd.DataFrame(list_ch,columns=["busho_apr_id","tantou_apr_id","tantou_apr_name","juchu_day","result"])

    df_team=df[["busho_apr_id","tantou_apr_id","tantou_apr_name"]]
    df_team=df_team[df_team["busho_apr_id"].isin(["398","400","401","402"])]
    df_team=df_team.drop_duplicates()

    # 個人
    df_team=df_team.set_index("tantou_apr_id") 
    df_all=df[["tantou_apr_id","juchu_day"]].groupby("tantou_apr_id").count()
    df_detail=df.pivot_table(index=["tantou_apr_id"],columns="result",values="juchu_day",aggfunc="count",fill_value=0)

    df_last=pd.merge(df_team,df_all,on="tantou_apr_id")
    df_last=pd.merge(df_last,df_detail,on="tantou_apr_id")

    for i in range(8):
        try:
            df_last[str(i)+"_p"]=df_last[str(i)] / df_last["juchu_day"] * 100
        except:
            df_last[str(i)+"_p"]=0

    try:
        df_last["sumi"]=df_last["juchu_day"] - df_last["0"]
    except:
        df_last["sumi"]=df_last["juchu_day"]
    df_last["sumi_p"]=df_last["sumi"] / df_last["juchu_day"] * 100

    df_last.index=df_last.index.astype(int)
    df_last=df_last.sort_index() 
    last_list=df_last.to_dict(orient='index')

    # チーム
    df_last2=df_last.reset_index()
    df_last2=df_last2.drop(["tantou_apr_name","tantou_apr_id"],axis=1)
    df_last2=df_last2.groupby("busho_apr_id").sum()
    for i in range(8):
        try:
            df_last2[str(i)+"_p"]=df_last2[str(i)] / df_last2["juchu_day"] * 100
        except:
            df_last2[str(i)+"_p"]=0

    try:
        df_last2["sumi"]=df_last2["juchu_day"] - df_last2["0"]
    except:
        df_last2["sumi"]=df_last2["juchu_day"]
    df_last2["sumi_p"]=df_last2["sumi"] / df_last2["juchu_day"] * 100

    last_list2=df_last2.to_dict(orient='index')

    # その他
    apr_list=Approach_list.objects.filter(action=1)

    # アクティブ担当
    try:
        act_id=request.session["search"]["tantou"]
        if act_id=="":
            act_user="担当者が未設定です"
        else:
            act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    except:
        pass

    params={
        "apr_list":apr_list,
        "last_list":last_list,
        "last_list2":last_list2,
        "ses":ses,
        "act_user":act_user,
    }
    return render(request,"apr/shukei.html",params)


# 集計ボタン
def shukei_click(request):
    sh_type=request.POST["shurui"]
    if sh_type=="han":
        request.session["han_apr_shukei"]["shukei_id"]="0"
    elif sh_type=="nou":
        request.session["han_apr_shukei"]["shukei_id"]="N"
    elif sh_type=="apr":
        request.session["han_apr_shukei"]["shukei_id"]=request.POST["choice_approach_id"]

    request.session["han_apr_shukei"]["shukei_month"]=request.POST["shukei_month"]
    return redirect("apr:shukei_index")