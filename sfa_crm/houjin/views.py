from django.shortcuts import render,redirect
from .models import Houjin_gaishou
from sfa.models import Sfa_data,Member
from django.http import JsonResponse
import datetime
import calendar
import jpholiday
import io
import csv
from django.http import HttpResponse
import urllib.parse
from django.db.models import IntegerField
from django.db.models.functions import Cast



# 担当別_発送履歴カレンダー
def calendar_index(request):
    if "houjin_tantou_id" not in request.session:
        request.session["houjin_tantou_id"]=""

    # 発送年月
    if request.method=="GET":
        mon=datetime.date.today().strftime("%Y-%m")
        tantou_id=request.session["houjin_tantou_id"]
    else:
        mon=request.POST["hassou_month"]
        tantou_id=request.POST["tantou_id"]
    
    y=int(mon[:4])
    m=int(mon[-2:])
    last_day=calendar.monthrange(y,m)[1]

    str_mon=""
    for i in range(1,last_day+1):
        day=datetime.date(y,m,i)

        # 土日祝
        if jpholiday.is_holiday(day):
            if day.weekday() == 6:
                str_mon += "<tr style='height: 100px;'><td style='background-color: #ffe3f1;'><div style='color: #ff0000; font-weight: bold;'>" + str(i) + "</div>"
            else:
                str_mon += "<td style='background-color: #ffe3f1;'><div style='color: #ff0000; font-weight: bold;'>" + str(i) + "</div>"
        elif day.weekday() == 6:
            str_mon += "<tr style='height: 100px;'><td style='background-color: #ffe3f1;'><div style='color: #ff0000; font-weight: bold;'>" + str(i) + "</div>"
        elif day.weekday() == 5:
            str_mon += "<td style='background-color: #c6ffff;'><div style='color: #0000ff; font-weight: bold;'>" + str(i) + "</div>"
        else:
            str_mon += "<td><div style='font-weight: bold;'>" + str(i) + "</div>"

        # 発送履歴
        ins=Sfa_data.objects.filter(hassou_day=day,tantou_id=tantou_id)
        for h in ins:
            if h.money > 0:
                com=h.com or ""
                com_busho=h.com_busho or ""
                sei=h.sei or ""
                mei=h.mei or ""
                str_mon += "<a href='" + h.mitsu_url + "' target='_blank'><div class='houjin_calendar'>" \
                            + com + "　" + com_busho + "　" + sei + mei + "<br>" + f"{h.money:,}" + "円</div></a>"
                
        str_mon += "</td>"

        # 行の最終
        if day.weekday()==5:
            str_mon += "</tr>"

    # 第１週と最終週
    mon_day_1=datetime.date(y,m,1).weekday()
    if mon_day_1 != 6:
        str_mon = "<tr style='height: 100px;'><td colspan='" +  str(mon_day_1 + 1) + "' style='background-color: #f1f1f1;'></td>" + str_mon

    mon_day_last=datetime.date(y,m,last_day).weekday()
    if mon_day_last == 6:
        str_mon += "<td colspan='6' style='background-color: #f1f1f1;'></td></tr>"
    elif mon_day_last != 5:
        str_mon += "<td colspan='" + str(5 - mon_day_last) + "' style='background-color: #f1f1f1;'></td></tr>"

    str_mon=str_mon.replace("　　","　")

    # 担当者
    tantou_list=Member.objects.filter(houjin=1)

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    params={
        "calendar_body":str_mon,
        "hassou_month":mon,
        "tantou_list":tantou_list,
        "tantou_id":tantou_id,
        "act_user":act_user,
        }
    return render(request,"houjin/tantou_calendar.html",params)


# 法人外商リスト_取込
def houjin_gaishou_imp(request):
    imp_type=request.POST["imp_type"]
    data = io.TextIOWrapper(request.FILES['csv3'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    h=0
    for i in csv_list:
        if h!=0:
              Houjin_gaishou.objects.create(
                imp_type=imp_type,
                imp_day=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                recieve_day=i[0],
                kubun=i[1],
                houjin_com=i[2],
                houjin_busho=i[3],
                houjin_tantou=i[4],
                houjin_tel=i[5],
                houjin_mail=i[6],
                houjin_address=i[7],
                houjin_comment=i[8],
              )
        h+=1

    if imp_type=="0":
        return render(request,"apr/approach_list.html",{"ans3":"yes"})
    else:
        return redirect("houjin:houjin_gaishou_index")


# 法人外商ボード_index
def houjin_gaishou_index(request):
    if "houjin_gaishou" not in request.session:
        request.session["houjin_gaishou"]={}
    if "busho" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["busho"]=""
    if "tantou" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["tantou"]=""
    if "com" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["com"]=""
    if "name" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["name"]=""
    if "tel" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["tel"]=""
    if "mail" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["mail"]=""
    if "recieve_day" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["recieve_day"]=""
    if "kubun" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["kubun"]=""
    if "day_st" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["day_st"]=""
    if "day_ed" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["day_ed"]=""
    if "act_st" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["act_st"]=""
    if "act_ed" not in request.session["houjin_gaishou"]:
        request.session["houjin_gaishou"]["act_ed"]=""

    ses=request.session["houjin_gaishou"]
    tantou_list=Member.objects.filter(busho_id=ses["busho"],houjin=1).annotate(num=Cast("tantou_id",IntegerField())).order_by("num")
    itaku_result=["","アポ","資料送付","お断り","その他"]
    kubun_list=list(Houjin_gaishou.objects.all().values_list("kubun",flat=True).order_by("kubun").distinct())

    # アクティブ担当
    act_id=request.session["search"]["tantou"]
    if act_id=="":
        act_user="担当者が未設定です"
    else:
        act_user=Member.objects.get(tantou_id=act_id).busho + "：" + Member.objects.get(tantou_id=act_id).tantou

    # 操作者
    sousa_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sousa_busho=Member.objects.get(tantou_id=act_id).busho
        sousa_tantou=Member.objects.get(tantou_id=act_id).tantou
    except:
        sousa_busho=""
        sousa_tantou="不明"
    print(sousa_time,sousa_busho,sousa_tantou,"■ 新規開拓ボード")

    params={
        "busho_list":{"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"},
        "tantou_list":tantou_list,
        "itaku_result":itaku_result,
        "kubun_list":kubun_list,
        "ses":ses,
        "act_user":act_user,
    }
    return render(request,"houjin/gaishou.html",params)


# 法人外商ボード_load
def houjin_gaishou_load(request):
    col_name={
        "0":"未対応",
        "1":"TEL入れ",
        "2":"資料送付",
        "3":"アポ打診",
        "4":"外商（来店）調整 / アポ確定",
        "5":"案件化（顧客管理に移管）",
        "6":"中止（音信不通等）",
        }
    
    # フィルター
    ses=request.session["houjin_gaishou"]
    fil={}
    if ses["busho"] != "":
        fil["busho_id"]=ses["busho"]
    if ses["tantou"] != "":
        fil["tantou_id"]=ses["tantou"]
    if ses["kubun"] != "":
        fil["kubun"]=ses["kubun"]
    if ses["com"] != "":
        fil["houjin_com__contains"]=ses["com"].strip()
    if ses["name"] != "":
        fil["houjin_tantou__contains"]=ses["name"].strip()
    if ses["tel"] != "":
        fil["houjin_tel"]=ses["tel"]
    if ses["mail"] != "":
        fil["houjin_mail"]=ses["mail"]
    if ses["day_st"] != "":
        fil["recieve_day__gte"]=ses["day_st"] + " 00:00:00"
    if ses["day_ed"] != "":
        fil["recieve_day__lte"]=ses["day_ed"] + " 23:59:59"
    if ses["act_st"] != "":
        fil["last_act__gte"]=ses["act_st"]
    if ses["act_ed"] != "":
        fil["last_act__lte"]=ses["act_ed"]

    dataContent=[]
    for key,val in col_name.items():
        
        # 未対応は常に表示
        if key == "0":
            ins=Houjin_gaishou.objects.filter(boad_col="0").order_by("boad_row")
        else:
            fil["boad_col"]=key
            ins=Houjin_gaishou.objects.filter(**fil).order_by("boad_row")

        # カラムごとにボードを作成
        item=[]
        for h in ins:
            
            if h.kubun=="カイタク":
                card_type="<div class='houjin_card_1'>"
            elif h.kubun=="active call":
                card_type="<div class='houjin_card_2'>"
            else:
                card_type="<div class='houjin_card_3'>"

            # 担当者img
            t_busho=""
            if h.busho_id=="398":
                t_busho="houjin_tantou_tokyo"
            elif h.busho_id=="400":
                t_busho="houjin_tantou_osaka"
            elif h.busho_id=="401":
                t_busho="houjin_tantou_takamatsu"
            elif h.busho_id=="402":
                t_busho="houjin_tantou_fukuoka"

            t_font=""
            if h.tantou_id != None and h.tantou_id != "":
                t_sei=h.tantou.split()[0]
                if len(t_sei)==1:
                    t_font="style='font-size: 1.8em;'"
                elif len(t_sei)==2:
                    t_font="style='font-size: 1.1em;'"
                else:
                    t_font="style='font-size: 0.9em;'"  
            else:
                t_sei=""

            tantou_img="<div class='houjin_tantou " + t_busho + "' " + t_font + ">" + t_sei + "</div>"

            # その他
            if h.tantou_id != None and h.tantou_id != "":
                tantou_name=h.tantou
            else:
                tantou_name=""

            if h.last_act != None and h.last_act != "":
                last_act=h.last_act
            else:
                last_act=""

            if h.bikou != None and h.bikou != "":
                bikou=h.bikou
            else:
                bikou=""
                

            title_str = card_type \
                + "<div class='flex'>" \
                    + "<div style='width: 70px;'>" + tantou_img + "</div>" \
                    + "<div style='font-size: 0.9em;'>" \
                        + "<div><i class='bi bi-envelope-open'></i> " + h.recieve_day + "</div>" \
                        + "<div><i class='bi bi-building'></i> " + h.kubun + "</div>" \
                    + "</div>" \
                + "</div>" \
                + "<div style='margin-top: 10px; font-weight: bold;'>" \
                    + "<div>" + h.houjin_com + "</div>" \
                    + "<div>" + h.houjin_busho + "</div>" \
                    + "<div>" + h.houjin_tantou + "</div>" \
                + "</div>" \
                + "<div style='font-size: 0.9em;'>" \
                    + "<div style='margin-top: 5px;'>" \
                        + "<button type='button' class='btn btn-outline-success btn-sm'" \
                            + "id='" + str(h.id) + "' name='gaishou_boad' data-bs-toggle='modal' data-bs-target='#modal_gaishou'>" \
                            + "<i class='bi bi-pencil-square'></i> 詳細を確認 / 編集する" \
                        + "</button>" \
                    + "</div>" \
                    + "<div style='margin-top: 5px;'>" \
                        + "<div class='flex'>" \
                            + "<div style='width: 60px;'>担当者：</div>" \
                            + "<div>" + tantou_name + "</div>" \
                        + "</div>" \
                        + "<div class='flex'>" \
                            + "<div style='width: 115px;'>最終アクション日：</div>" \
                            + "<div>" + last_act + "</div>" \
                        + "</div>" \
                        + "<div style='margin-top:5px'><textarea style='width: 100%; font-size: 0.8em;' rows='3' readonly>" + bikou + "</textarea>" \
                    + "</div>" \
                + "</div>" \
                + "</div>"

            item.append({"id":h.id,"title":title_str})

        title=val + "<br><span style='font-size:0.8em; font-weight:lighter;'>\
                        ■ <span id='column_" + key + "_count'>" + str(ins.count()) + "</span>件</span>"
        
        dataContent.append({"id":"column_" + key,"title":title,"item":item})

    d={"dataContent":dataContent}
    return JsonResponse(d)


# 法人外商ボード_移動
def houjin_gaishou_move(request):
    column=request.POST.get("target_column")
    index_list=request.POST.get("col_index")
    column_num=column.replace("column_","")
    index_list=eval(index_list)

    for i,h in enumerate(index_list):
        ins=Houjin_gaishou.objects.get(id=h)
        ins.boad_col=column_num
        ins.boad_row=i
        ins.save()

    col_count=[]
    for i in range(6):
        col_count.append(str(i) + "_" + str(Houjin_gaishou.objects.filter(boad_col=str(i)).count()))

    d={"col_count":col_count}
    return JsonResponse(d)


# 法人外商ボード_モーダル表示用
def houjin_gaishou_detail(request):
    gaishou_id=request.POST.get("gaishou_id")
    ins=list(Houjin_gaishou.objects.filter(id=gaishou_id).values())[0]
    modal_tantou_list=list(Member.objects.filter(busho_id=ins["busho_id"],houjin=1).annotate(num=Cast("tantou_id",IntegerField())).order_by("num").values())
    d={"detail":ins,"modal_tantou_list":modal_tantou_list}
    return JsonResponse(d)


# 法人外商ボード_保存
def houjin_gaishou_save(request):
    gaishou_id=request.POST.get("gaishou_id")
    busho_id=request.POST.get("busho_id")
    tantou_id=request.POST.get("tantou_id")
    last_act=request.POST.get("last_act")
    bikou=request.POST.get("bikou")
    itaku_result=request.POST.get("itaku_result")

    ins=Houjin_gaishou.objects.get(id=gaishou_id)
    ins.busho_id=busho_id
    busho_list={"":"","398":"東京チーム","400":"大阪チーム","401":"高松チーム","402":"福岡チーム"}
    ins.busho=busho_list[busho_id]
    ins.tantou_id=tantou_id
    if tantou_id != "":
        ins.tantou=Member.objects.get(tantou_id=tantou_id).tantou
    else:
        ins.tantou=None
    ins.bikou=bikou
    ins.itaku_result=itaku_result
    ins.last_act=last_act
    ins.save()

    d={}
    return JsonResponse(d)


# 法人外商ボード_部署選択
def houjin_gaishou_busho(request):
    busho_id=request.POST.get("busho")
    tantou=list(Member.objects.filter(busho_id=busho_id,houjin=1).annotate(num=Cast("tantou_id",IntegerField())).order_by("num").values())
    d={"tantou":tantou}
    return JsonResponse(d)


# 法人外商ボード_検索
def houjin_gaishou_search(request):
    request.session["houjin_gaishou"]["busho"]=request.POST["busho"]
    request.session["houjin_gaishou"]["tantou"]=request.POST["tantou"]
    request.session["houjin_gaishou"]["kubun"]=request.POST["kubun"]
    request.session["houjin_gaishou"]["com"]=request.POST["com"]
    request.session["houjin_gaishou"]["name"]=request.POST["name"]
    request.session["houjin_gaishou"]["tel"]=request.POST["tel"]
    request.session["houjin_gaishou"]["mail"]=request.POST["mail"]
    request.session["houjin_gaishou"]["day_st"]=request.POST["day_st"]
    request.session["houjin_gaishou"]["day_ed"]=request.POST["day_ed"]
    request.session["houjin_gaishou"]["act_st"]=request.POST["act_st"]
    request.session["houjin_gaishou"]["act_ed"]=request.POST["act_ed"]
    return redirect("houjin:houjin_gaishou_index")


# 法人外商ボード_CSV出力
def houjin_gaishou_csv(request):
    kubun=request.POST["csv_kubun"]
    day_st=request.POST["csv_day_st"]
    day_ed=request.POST["csv_day_ed"]

    ins=Houjin_gaishou.objects.filter(kubun=kubun,recieve_day__gte= day_st + " 00:00", recieve_day__lte= day_ed + " 23:59")
    recieve_list=[["日付","会社名","内容","メモ"]]
    for i in ins:
        try:
            i.bikou.encode("CP932")
            recieve_list.append([i.recieve_day[:10],i.houjin_com,i.itaku_result,i.bikou])
        except:
            recieve_list.append([i.recieve_day[:10],i.houjin_com,i.itaku_result,"備考に特殊文字が含まれているため出力できません。"])

    filename=urllib.parse.quote(kubun + "_報告用.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in recieve_list:
        writer.writerow(line)

    return response