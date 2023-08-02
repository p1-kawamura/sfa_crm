from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action
import csv
import io
from datetime import date


def index(request):
    ins=Sfa_data.objects.all()
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
    return render(request,"sfa/index.html",{"list":list})


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
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.status=status
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


# 元DB取込
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
                    "cus_id":i[12],
                    "sei":i[13],
                    "mei":i[14],
                    "mail":i[15],
                    "pref":i[16],
                    "com":i[17],
                    "keiro":i[18],
                    "money":i[19],
                    "kakudo":i[20]
                }            
            )
        h+=1
    return render(request,"sfa/index.html")