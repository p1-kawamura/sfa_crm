from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Sfa_data,Sfa_action,Member
import csv
import io
import json
from datetime import date
from django.http import HttpResponse
import urllib.parse
from django.db.models import Sum


def index(request):
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
    if "mw_list" not in request.session:
        request.session["mw_list"]=[]
    if "crm_mw_list" not in request.session:
        request.session["crm_mw_list"]=[]

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
    
    ins=Sfa_data.objects.filter(**fil).order_by("mitsu_day")
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
        d={"見積中":"見","見積送信":"見","イメージ":"イ","受注":"受","発送完了":"発","キャンセル":"キ","終了":"終","保留":"保","失注":"失","連絡待ち":"待"}
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

    tantou_list=Member.objects.filter(busho_id=ses["busho"])
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    
    params={
        "list":list,
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":tantou_list,
        "chumon_kubun":["","新規","追加","追加新柄","刷り直し","返金"],
        "kakudo_list":["","A","B","C"],
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "status_list":["見積中","見積送信","イメージ","受注","発送完了","キャンセル","終了","保留","失注","連絡待ち"],
        "ses":ses,
        "act_user":act_user,
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
    busho_id=request.POST.get("busho")
    tantou=list(Member.objects.filter(busho_id=busho_id).values())
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
    mw=request.POST.get("mw")
    status=request.POST.get("status")
    bikou=request.POST.get("bikou")
    ins=Sfa_data.objects.get(mitsu_id=mitsu_id)
    ins.kakudo=kakudo
    ins.status=status
    ins.bikou=bikou
    if mw=="true":
        ins.mw=1
    else:
        ins.mw=0
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
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
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
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/show.html",{"list":ins,"mitsu_num":mitsu_num,"com":com,"name":name,"act_user":act_user})


# メールワイズ_表示ページ
def mw_page(request):
    busho_id=request.session["search"]["busho"]
    arr={"398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    busho=arr[busho_id]
    ins=Sfa_data.objects.filter(busho_id=busho_id,show=0,mw=1).order_by("tantou_id")
    member=Member.objects.all()
    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou
    return render(request,"sfa/mw_csv.html",{"busho":busho,"list":ins,"member":member,"act_user":act_user})


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
        ins.save()
    filename=urllib.parse.quote("【案件管理】メールワイズ用リスト.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in mw_csv:
        writer.writerow(line)
    return response


# 確度集計
def kakudo_index(request):
    #全体
    all=[]
    for i in ["A","B","C",""]:
        li=[]
        all_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i).count()
        li.append(all_count)
        all_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i).aggregate(Sum("money"))
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
        for i in ["A","B","C",""]:
            li=[]
            team_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,busho_id=key).count()
            li.append(team_count)
            team_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=i,busho_id=key).aggregate(Sum("money"))
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
            for h in ["A","B","C",""]:
                li=[]
                person_count=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=h,tantou_id=i).count()
                li.append(person_count)
                person_money=Sfa_data.objects.filter(show=0,status__in=["見積中","見積送信","イメージ"],kakudo=h,tantou_id=i).aggregate(Sum("money"))
                if person_money["money__sum"] != None:
                    li.append(person_money["money__sum"])
                else:
                    li.append(0)
                kaku_li.append(li)
            person_li.append(kaku_li)
        person[value]=person_li

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={"all":all,"team":team,"person":person,"act_user":act_user}
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
    Member.objects.all().delete()
    return redirect("sfa:index")