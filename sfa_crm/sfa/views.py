from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action,Member
import csv
import io
import json
from datetime import date
import datetime


def index(request):
    print(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
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
    if "pref" not in request.session["search"]:
        request.session["search"]["pref"]=""
    if "kakudo" not in request.session["search"]:
        request.session["search"]["kakudo"]=""
    if "st" not in request.session["search"]:
        request.session["search"]["st"]=[]

    ses=request.session["search"]
    fil={}
    fil["tantou_id"]=ses["tantou"]
    fil["show"]=0
    if ses["chumon_kubun"] != "":
        fil["order_kubun"]=ses["chumon_kubun"]
    if ses["pref"] != "":
        fil["pref"]=ses["pref"]
    if ses["kakudo"] != "":
        fil["kakudo"]=ses["kakudo"]
    if len(ses["st"])!=0:
        fil["status__in"]=ses["st"]
    
    ins=Sfa_data.objects.filter(**fil)
    list=[]
    for i in ins:
        dic={}
        dic["mitsu_id"]=i.mitsu_id
        dic["cus_id"]=i.cus_id
        dic["mitsu_day"]=i.mitsu_day[5:].replace("-","/")
        dic["mitsu_num"]=i.mitsu_num + "-" + i.mitsu_ver
        dic["order_kubun"]=i.order_kubun
        dic["keiro"]=i.keiro[:1]
        dic["use_kubun"]=i.use_kubun[:1]
        d={"チームウェア・アイテム":"チ","制服・スタッフウェア":"制","販促・ノベルティ":"ノ",
          "記念品・贈答品":"記","販売":"販","自分用":"自","その他":"他","":""}
        dic["use_youto"]=d[i.use_youto]
        dic["pref"]=i.pref
        dic["com"]=i.com
        dic["cus"]=i.sei + i.mei
        d={"見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","終了":"終","失注":"失","連絡待ち":"待"}
        dic["status"]=d[i.status]
        dic["money"]=i.money
        if i.nouhin_kigen != "":
            dic["nouki"]="期限：" + i.nouhin_kigen[5:].replace("-","/")
        elif i.nouhin_shitei != "":
            dic["nouki"]="指定：" +i.nouhin_shitei[5:].replace("-","/")
        else:
            dic["nouki"]=""
        dic["kakudo"]=i.kakudo
        dic["juchu"]=i.juchu_day[5:].replace("-","/")
        dic["hassou"]=i.hassou_day[5:].replace("-","/")

        tel_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=1).count() 
        if tel_count > 0:
            act_tel=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=1).latest("day")
            dic["tel"]=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            if act_tel.tel_result=="対応":
                dic["tel_result"]=1
            else:
                dic["tel_result"]=2
        else:
            dic["tel_result"]=0

        mail_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=2).count()
        if mail_count > 0:
            act_mail=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=2).latest("day")
            dic["mail"]=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ") "
            dic["mail_result"]=1
        else:
            dic["mail_result"]=0

        today=str(date.today())
        alert_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=4,alert_check=0,day__lte=today).count()
        dic["alert"]=alert_count

        list.append(dic)

    tantou_list=Member.objects.filter(busho=ses["busho"])
    params={
        "list":list,
        "busho_list":["","東京チーム","大阪チーム","高松チーム","福岡チーム"],
        "tantou_list":tantou_list,
        "chumon_kubun":["","新規","追加","追加新柄"],
        "kakudo_list":["","A","B","C"],
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "status_list":["見積中","見積送信","イメージ","受注","発送完了","キャンセル","終了","保留","失注","連絡待ち"],
        "ses":ses,
    }
    return render(request,"sfa/index.html",params)


# 案件検索
def search(request):
    busho=request.POST["busho"]
    tantou=request.POST["tantou"]
    chumon_kubun=request.POST["chumon_kubun"]
    pref=request.POST["pref"]
    kakudo=request.POST["kakudo"]
    st=request.POST.getlist("st")

    request.session["search"]["busho"]=busho
    request.session["search"]["tantou"]=tantou
    request.session["search"]["chumon_kubun"]=chumon_kubun
    request.session["search"]["pref"]=pref
    request.session["search"]["kakudo"]=kakudo
    request.session["search"]["st"]=st
    return redirect("sfa:index")


# 部署選択（対象担当者表示）
def busho_tantou(request):
    busho=request.POST.get("busho")
    tantou=list(Member.objects.filter(busho=busho).values())
    d={"tantou":tantou}
    return JsonResponse(d)


# モーダルで詳細表示
def mitsu_detail_api(request):
    mitsu_id=request.POST.get("mitsu_id")
    res=list(Sfa_data.objects.filter(mitsu_id=mitsu_id).values())[0]
    res2=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
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
    d={"res":res,"res2":res2,"res3":res3,"text":text,"alert_num":alert_num}
    return JsonResponse(d)


# モーダル上部（確度、ステータス、メールワイズ）
def modal_top(request):
    mitsu_id=request.POST.get("mitsu_id")
    kakudo=request.POST.get("kakudo")
    status=request.POST.get("status")
    bikou=request.POST.get("bikou")
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.status=status
    ins.bikou=bikou
    ins.save()
    d={}
    return JsonResponse(d)


# モーダル下部（電話、メール、備考、アラート）
def modal_bot(request):
    mitsu_id=request.POST.get("mitsu_id")
    day=request.POST.get("day")
    type=request.POST.get("type")
    tel_result=request.POST.get("tel_result")
    text=request.POST.get("text")
    if type=="1":
        Sfa_action.objects.create(mitsu_id=mitsu_id,day=day,type=type,tel_result=tel_result,text=text)
    else:
        Sfa_action.objects.create(mitsu_id=mitsu_id,day=day,type=type,text=text)
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
        else:
            ins.show=1
        ins.save()
    d={}
    return JsonResponse(d)


# 案件表示_初期ページ
def show_index(request):
    return render(request,"sfa/show.html")


# 案件表示_結果ページ
def show(request):
    mitsu_num=request.session["mitsu_num"]
    ins=Sfa_data.objects.filter(mitsu_num=mitsu_num)
    for i in ins:
        com=i.com
        name=i.sei +" " + i.mei
        break
    return render(request,"sfa/show.html",{"list":ins,"mitsu_num":mitsu_num,"com":com,"name":name})



# 元DB取込
def csv_imp_page(request):
    return render(request,"sfa/csv_imp.html")


def csv_imp(request):

    #見積リスト
    data = io.TextIOWrapper(request.FILES['csv1'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)
        
    h=0
    for i in csv_list:
        if h!=0:
            Sfa_data.objects.update_or_create(
                mitsu_id=i[0],
                defaults={
                    "mitsu_id":i[0],
                    "mitsu_num":i[1],
                    "mitsu_ver":i[2],
                    "status":i[3],
                    "order_kubun":i[4],
                    "use_kubun":i[5],
                    "use_youto":i[6],
                    "nouhin_kigen":i[7],
                    "nouhin_shitei":i[8],
                    "mitsu_day":i[9],
                    "juchu_day":i[10],
                    "hassou_day":i[11],
                    "tantou_id":i[12],
                    "busho_id":i[13],
                    "cus_id":i[14],
                    "sei":i[15],
                    "mei":i[16],
                    "mail":i[17],
                    "pref":i[18],
                    "com":i[19],
                    "tel":i[20],
                    "tel_mob":i[21],
                    "pay":i[22],
                    "keiro":i[23],
                    "money":i[24],
                }            
            )
        h+=1

    # #担当リスト
    # data = io.TextIOWrapper(request.FILES['csv2'].file, encoding="cp932")
    # csv_content = csv.reader(data)
    # csv_list=list(csv_content)
        
    # h=0
    # for i in csv_list:
    #     if h!=0:
    #         Member.objects.update_or_create(
    #             tantou_id=i[2],
    #             defaults={
    #                 "busho":i[0],
    #                 "tantou":i[1],
    #                 "tantou_id":i[2],
    #             }            
    #         )
    #     h+=1

    return render(request,"sfa/csv_imp.html",{"message":"取込が完了しました！"})