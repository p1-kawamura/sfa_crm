from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action,Member
import csv
import io
import json
import requests
from datetime import date
from django.http import HttpResponse
import urllib.parse
from django.db.models import Sum
from datetime import datetime


def index_api(request):
    if "tantou" in request.session["search"]:
        tantou_id=request.session["search"]["tantou"]
        last_api=Member.objects.get(tantou_id=tantou_id).last_api
        url="https://core-sys.p1-intl.co.jp/p1web/v1/estimations/?handledById=" + tantou_id + "&updatedAtFrom=" + last_api
        res=requests.get(url)
        res=res.json()
        res=res["estimations"]
        for i in res:
            Sfa_data.objects.update_or_create(
            mitsu_id=i["id"],
            defaults={
                "mitsu_id":i["id"],
                "mitsu_num":i["number"],
                "mitsu_ver":i["version"],
                "mitsu_url":i["estimationPageUrl"],
                "order_kubun":i["orderType"],
                "use_kubun":i["persona"],
                "use_youto":i["purpose"],
                "nouhin_kigen":i["deliveryLimitDate"],
                "nouhin_shitei":i["deliveryAppointedDate"],
                "make_day":i["createdAt"],
                "mitsu_day":i["firstEstimationDate"],
                "update_day":i["updatedAt"],
                "juchu_day":i["orderReceivedDate"],
                "hassou_day":i["shippedDate"],
                "cus_id":i["customerId"],
                "sei":i["ordererNameLast"],
                "mei":i["ordererNameFirst"],
                "tel":i["ordererTel"],
                "tel_mob":i["ordererMobilePhone"],
                "mail":i["ordererEmailMain"],
                "pref":i["ordererPrefecture"],
                "com":i["ordererCorporateName"],
                "com_busho":i["ordererDepartmentName"],
                "keiro":i["comingRoute"],
                "money":i["totalPrice"],
                "pay":i["paymentMethod"],
                "busho_id":i["handledDepartmentId"],
                "tantou_id":i["handledById"],
                }
            )
            # ステータス
            ins=Sfa_data.objects.get(mitsu_id=i["id"])
            if ins.status not in ["失注","連絡待ち","サンクス"]:
                ins.status=i["status"]
                ins.save()

    return redirect("sfa:index")


def index(request):
    # request.session.clear()
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
    if "keiro" not in request.session["search"]:
        request.session["search"]["keiro"]=""
    if "pref" not in request.session["search"]:
        request.session["search"]["pref"]=""
    if "kakudo" not in request.session["search"]:
        request.session["search"]["kakudo"]=""
    if "day_type" not in request.session["search"]:
        request.session["search"]["day_type"]="est" 
    if "day_st" not in request.session["search"]:
        request.session["search"]["day_st"]=""
    if "day_ed" not in request.session["search"]:
        request.session["search"]["day_ed"]=""
    if "st" not in request.session["search"]:
        request.session["search"]["st"]=[]
    if "sort_name" not in request.session["search"]:
        request.session["search"]["sort_name"]="mitsu_day"
    if "sort_jun" not in request.session["search"]:
        request.session["search"]["sort_jun"]="0"
    if "mw_list" not in request.session:
        request.session["mw_list"]=[]
    if "crm_mw_list" not in request.session:
        request.session["crm_mw_list"]=[]
    if "kakudo_day" not in request.session:
        request.session["kakudo_day"]=datetime.now().strftime("%Y-%m")

    ses=request.session["search"]
    fil={}
    fil["tantou_id"]=ses["tantou"]
    fil["show"]=0
    if ses["chumon_kubun"] != "":
        fil["order_kubun"]=ses["chumon_kubun"]
    if ses["keiro"] != "":
        fil["keiro"]=ses["keiro"]
    if ses["pref"] != "":
        fil["pref"]=ses["pref"]
    if ses["kakudo"] != "":
        fil["kakudo"]=ses["kakudo"]
    if ses["day_type"]=="est":
        if ses["day_st"] != "":
            fil["make_day__gte"]=ses["day_st"]
        if ses["day_ed"] != "":
            fil["make_day__lte"]=ses["day_ed"]
    else:
        if ses["day_st"] != "":
            fil["hassou_day__gte"]=ses["day_st"]
        if ses["day_ed"] != "":
            fil["hassou_day__lte"]=ses["day_ed"]
    if len(ses["st"])!=0:
        fil["status__in"]=ses["st"]
    
    ins=Sfa_data.objects.filter(**fil)
    list=[]
    for i in ins:
        dic={}
        dic["mitsu_id"]=i.mitsu_id
        dic["mitsu_url"]=i.mitsu_url
        dic["cus_id"]=i.cus_id
        dic["make_day"]=i.make_day[5:].replace("-","/")
        dic["make_sort"]=i.make_day
        dic["mitsu_num"]=i.mitsu_num + "-" + i.mitsu_ver
        dic["order_kubun"]=i.order_kubun or ""
        if i.keiro != None:
            dic["keiro"]=i.keiro[:1]
        if i.use_kubun != None:
            dic["use_kubun"]=i.use_kubun[:1]
        if i.use_youto != None:
            d={"チームウェア・アイテム":"チ","制服・スタッフウェア":"制","販促・ノベルティ":"ノ",
            "記念品・贈答品":"記","販売":"販","自分用":"自","その他":"他","":""}
            dic["use_youto"]=d[i.use_youto]
        dic["pref"]=i.pref or ""
        dic["com"]=i.com or ""
        dic["cus"]=(i.sei or "") + (i.mei or "")
        d={"見積中":"見","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待","サンクス":"サ","":""}
        dic["status"]=d[i.status]
        dic["money"]=i.money
        if i.nouhin_kigen != None:
            dic["nouki"]="期限：" + i.nouhin_kigen[5:].replace("-","/")
            dic["nouki_sort"]=i.nouhin_kigen
        elif i.nouhin_shitei != None:
            dic["nouki"]="指定：" +i.nouhin_shitei[5:].replace("-","/")
            dic["nouki_sort"]=i.nouhin_shitei
        else:
            dic["nouki"]=""
            if ses["sort_jun"]=="0":
                dic["nouki_sort"]="2100-01-01"
            else:
                dic["nouki_sort"]="1900-01-01"
        if i.juchu_day != None:
            dic["juchu"]=i.juchu_day[5:].replace("-","/")
        if i.hassou_day != None:
            dic["hassou"]=i.hassou_day[5:].replace("-","/")
        if i.hassou_day != None:
            dic["hassou_sort"]=i.hassou_day
        else:
            if ses["sort_jun"]=="0":
                dic["hassou_sort"]="2100-01-01"
            else:
                dic["hassou_sort"]="1900-01-01"
        dic["kakudo"]=i.kakudo
        dic["mw"]=i.mw

        tel_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=1).count() 
        if tel_count > 0:
            act_tel=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=1).latest("day")
            dic["tel"]=act_tel.day[5:].replace("-","/") + " (" + str(tel_count) + ")"
            dic["tel_sort"]=act_tel.day
            if act_tel.tel_result=="対応":
                dic["tel_result"]=1
            else:
                dic["tel_result"]=2
        else:
            if ses["sort_jun"]=="0":
                dic["tel_sort"]="2100-01-01"
            else:
                dic["tel_sort"]="1900-01-01"
            dic["tel_result"]=0      

        mail_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=2).count()
        if mail_count > 0:
            act_mail=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=2).latest("day")
            dic["mail"]=act_mail.day[5:].replace("-","/") + " (" + str(mail_count) + ") "
            dic["mail_sort"]=act_mail.day
            dic["mail_result"]=1
        else:
            if ses["sort_jun"]=="0":
                dic["mail_sort"]="2100-01-01"
            else:
                dic["mail_sort"]="1900-01-01"
            dic["mail_result"]=0

        today=str(date.today())
        alert_count=Sfa_action.objects.filter(mitsu_id=i.mitsu_id,type=4,alert_check=0,day__lte=today).count()
        dic["alert"]=alert_count

        list.append(dic)

    # 並び替え
    if ses["sort_jun"]=="0":
        list=sorted(list,key=lambda x: x[ses["sort_name"]])
    else:
        list=sorted(list,key=lambda x: x[ses["sort_name"]], reverse=True)

    tantou_list=Member.objects.filter(busho_id=ses["busho"])

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    
    params={
        "list":list,
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":tantou_list,
        "chumon_kubun":["","新規","追加","追加新柄","刷り直し","返金"],
        "keiro_list":["","Web","Fax","Tel","来店","外商","法人問合せ"],
        "kakudo_list":["","A","B","C"],
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "status_list":["見積中","見積送信","イメージ","受注","発送完了","キャンセル","終了","保留","失注","連絡待ち","サンクス"],
        "sort_list":{"make_sort":"見積作成日","hassou_sort":"発送完了日","money":"金額","nouki_sort":"納期","tel_sort":"最終TEL","mail_sort":"最終メール"},
        "ses":ses,
        "act_user":act_user,
    }
    return render(request,"sfa/index.html",params)


# 案件検索
def search(request):
    busho=request.POST["busho"]
    tantou=request.POST["tantou"]
    chumon_kubun=request.POST["chumon_kubun"]
    keiro=request.POST["keiro"]
    pref=request.POST["pref"]
    kakudo=request.POST["kakudo"]
    day_type=request.POST["day_type"]
    day_st=request.POST["day_st"]
    day_ed=request.POST["day_ed"]
    st=request.POST.getlist("st")
    sort_name=request.POST["sort_name"]
    sort_jun=request.POST["sort_jun"]

    request.session["search"]["busho"]=busho
    request.session["search"]["tantou"]=tantou
    request.session["search"]["chumon_kubun"]=chumon_kubun
    request.session["search"]["keiro"]=keiro
    request.session["search"]["pref"]=pref
    request.session["search"]["kakudo"]=kakudo
    request.session["search"]["day_type"]=day_type
    request.session["search"]["day_st"]=day_st
    request.session["search"]["day_ed"]=day_ed
    request.session["search"]["st"]=st
    request.session["search"]["sort_name"]=sort_name
    request.session["search"]["sort_jun"]=sort_jun
    return redirect("sfa:index")


# 部署選択（対象担当者表示）
def busho_tantou(request):
    busho_id=request.POST.get("busho")
    tantou=list(Member.objects.filter(busho_id=busho_id).values())
    d={"tantou":tantou}
    return JsonResponse(d)


# モーダルで詳細表示
def mitsu_detail_api(request):
    mitsu_id=request.POST.get("mitsu_id")
    res=list(Sfa_data.objects.filter(mitsu_id=mitsu_id).values())[0]
    for i in res:
        if res[i]==None:
            res[i]=""
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


# モーダル上部（確度、ステータス）
def modal_top(request):
    mitsu_id=request.POST.get("mitsu_id")
    kakudo=request.POST.get("kakudo")
    kakudo_day=request.POST.get("kakudo_day")
    status=request.POST.get("status")
    bikou=request.POST.get("bikou")
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.kakudo_day=kakudo_day
    ins.status=status
    ins.bikou=bikou
    ins.save()
    d={}
    return JsonResponse(d)


# モーダル下部（電話、メール、備考、アラート）
def modal_bot(request):
    act_id=request.POST.get("act_id")
    mitsu_id=request.POST.get("mitsu_id")
    day=request.POST.get("day")
    type=request.POST.get("type")
    tel_result=request.POST.get("tel_result")
    text=request.POST.get("text")
    if act_id =="":
        if type=="1":
            Sfa_action.objects.create(mitsu_id=mitsu_id,day=day,type=type,tel_result=tel_result,text=text)
        else:
            Sfa_action.objects.create(mitsu_id=mitsu_id,day=day,type=type,text=text)
    else:
        ins=Sfa_action.objects.get(act_id=act_id)
        ins.type=type
        ins.day=day
        if type=="1":
            ins.tel_result=tel_result
        ins.text=text
        ins.save()
    res=list(Sfa_action.objects.filter(mitsu_id=mitsu_id).order_by("day").values())
    d={"res":res}
    return JsonResponse(d)


# モーダル下部_クリック
def modal_bot_click(request):
    act_id=request.POST.get("act_id")
    ins=Sfa_action.objects.get(act_id=act_id)
    res={"type":ins.type,"tel":ins.tel_result,"day":ins.day,"text":ins.text}
    d={"res":res}
    return JsonResponse(d)


# モーダル下部_削除
def modal_bot_delete(request):
    act_id=request.POST.get("act_id")
    mitsu_id=request.POST.get("mitsu_id")
    Sfa_action.objects.get(act_id=act_id).delete()
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
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/show.html",{"act_user":act_user})


# 案件表示_結果ページ
def show(request):
    mitsu_num=request.session["mitsu_num"]
    ins=Sfa_data.objects.filter(mitsu_num=mitsu_num)
    for i in ins:
        com=i.com
        name=i.sei +" " + i.mei
        break
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/show.html",{"list":ins,"mitsu_num":mitsu_num,"com":com,"name":name,"act_user":act_user})


# メールワイズ_表示ページ
def mw_page(request):
    busho_id=request.session["search"]["busho"]
    arr={"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    busho=arr[busho_id]
    ins=Sfa_data.objects.filter(busho_id=busho_id,show=0,mw=1).order_by("tantou_id")
    member=Member.objects.all()
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/mw_csv.html",{"busho":busho,"list":ins,"member":member,"act_user":act_user})


# メールワイズ_追加
def mw_add(request):
    mw_add_list=request.POST.get("mw_list")
    mw_add_list=json.loads(mw_add_list)
    for i in mw_add_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.mw=1
        ins.save()
    d={}
    return JsonResponse(d)


# メールワイズ_削除ボタン
def mw_delete(request,pk):
    ins=Sfa_data.objects.get(pk=pk)
    ins.mw=0
    ins.save()
    return redirect("sfa:mw_page")


#メールワイズ_CSV準備
def mw_make(request):
    mw_list=request.POST.get("list")
    mw_list=json.loads(mw_list)
    request.session["mw_list"]=mw_list
    d={}
    return JsonResponse(d)


# メールワイズ_DL
def mw_download(request):
    mw_list=request.session["mw_list"]
    mw_csv=[]
    for i in mw_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        a=[
            ins.com, #会社
            ins.sei + ins.mei, #氏名
            ins.mail , #メールアドレス
            Member.objects.get(tantou_id=ins.tantou_id).tantou, #担当
        ]
        mw_csv.append(a)
        ins.mw=0
        ins.status="サンクス"
        ins.save()
    filename=urllib.parse.quote("【案件】メールワイズ用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response


# 一覧から非表示
def show_list_direct(request):
    show_list=request.POST.get("show_list")
    show_list=json.loads(show_list)
    for i in show_list:
        ins=Sfa_data.objects.get(mitsu_id=i)
        ins.show=1
        ins.save()
    d={}
    return JsonResponse(d)


# 確度集計
def kakudo_index(request):
    if request.method=="GET":
        kakudo_day=request.session["kakudo_day"]
    else:
        kakudo_day=request.POST["kakudo_day"]
        request.session["kakudo_day"]=kakudo_day

    #全体
    all=[]
    for i in ["A","B","C"]:
        li=[]
        all_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,kakudo_day=kakudo_day).count()
        li.append(all_count)
        all_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,kakudo_day=kakudo_day).aggregate(Sum("money"))
        if all_money["money__sum"] != None:
            li.append(all_money["money__sum"])
        else:
            li.append(0)
        all.append(li)

    #チーム
    busho_arr={"398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    team={}
    for key,value in busho_arr.items():
        team_li=[]
        for i in ["A","B","C"]:
            li=[]
            team_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,busho_id=key,kakudo_day=kakudo_day).count()
            li.append(team_count)
            team_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,busho_id=key,kakudo_day=kakudo_day).aggregate(Sum("money"))
            if team_money["money__sum"] != None:
                li.append(team_money["money__sum"])
            else:
                li.append(0)
            team_li.append(li)
        team[value]=team_li

    # 個人
    person={}
    for key,value in busho_arr.items():
        ins=Member.objects.filter(busho_id=key).values_list("tantou_id",flat=True)
        person_li=[]
        for i in ins:
            kaku_li=[]
            kaku_li.append(Member.objects.get(tantou_id=i).tantou)
            for h in ["A","B","C"]:
                li=[]
                person_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=h,tantou_id=i,kakudo_day=kakudo_day).count()
                li.append(person_count)
                person_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=h,tantou_id=i,kakudo_day=kakudo_day).aggregate(Sum("money"))
                if person_money["money__sum"] != None:
                    li.append(person_money["money__sum"])
                else:
                    li.append(0)
                kaku_li.append(li)
            person_li.append(kaku_li)
        person[value]=person_li

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={"all":all,"team":team,"person":person,"act_user":act_user,"kakudo_day":kakudo_day}
    return render(request,"sfa/kakudo.html",params)



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
                    "update_day":i[10],
                    "juchu_day":i[11],
                    "hassou_day":i[12],
                    "tantou_id":i[13],
                    "busho_id":i[14],
                    "cus_id":i[15],
                    "sei":i[16],
                    "mei":i[17],
                    "mail":i[18],
                    "pref":i[19],
                    "com":i[20],
                    "com_busho":i[21],
                    "tel":i[22],
                    "tel_mob":i[23],
                    "pay":i[24],
                    "keiro":i[25],
                    "money":i[26],
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
    #                 "busho_id":i[1],
    #                 "tantou":i[2],
    #                 "tantou_id":i[3],
    #             }            
    #         )
    #     h+=1

    return render(request,"sfa/csv_imp.html",{"message":"取込が完了しました！"})


#　DBクリア
def clear_sfa_data(request):
    Sfa_data.objects.all().delete()
    return redirect("sfa:index")

def clear_member(request):
    # Member.objects.all().delete()
    ins=Member.objects.all()
    for i in ins:
        i.last_api="2023-10-01 00:00:00"
        i.save()
    return redirect("sfa:index")