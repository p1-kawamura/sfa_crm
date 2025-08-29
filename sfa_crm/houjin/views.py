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


# 法人案件ボード
def houjin_index(request):
    col_name=["新規取込","商談誘発","見積・提案","納期・価格交渉","確定・入稿待ち","イメージ・校正","受注","納品","失注","保留","リサイクル"]
    return render(request,"houjin/houjin_index.html",{"col_name":col_name})


# 法人案件ボード_初期値
def houjin_load(request):
    col_name={
        "0":"新規取込",
        "1":"商談誘発",
        "2":"見積・提案",
        "3":"納期・価格交渉",
        "4":"確定・入稿待ち",
        "5":"イメージ・校正",
        "6":"受注",
        "7":"納品",
        "8":"失注",
        "9":"保留",
        "10":"リサイクル",
        }
    
    dataContent=[]
    for key,val in col_name.items():
        ins=Sfa_data.objects.filter(tantou_id="798",houjin_col=key,show=0).order_by("houjin_index")[:5]
        item=[]
        for h in ins:

            # 注文区分
            if h.order_kubun=="新規":
                order="<div class='order order_1'>新規</div>"
            elif h.order_kubun=="追加":
                order="<div class='order order_2'>追加</div>"
            elif h.order_kubun=="追加新柄":
                order="<div class='order order_3'>新追</div>"
            elif h.order_kubun=="刷り直し":
                order="<div class='order_4'>刷直</div>"
            elif h.order_kubun=="返金":
                order="<div class='order_4'>返金</div>"

            # 流入経路
            keiro=""
            if h.keiro != None:
                keiro="<div class='order_use'>" + h.keiro[:1] + "</div>"

            # 利用区分
            use=""
            if h.use_kubun != None:
                use="<div class='order_use'>" + h.use_kubun[:1] + "</div>"

            # 使用用途
            youto=""
            if h.s_use_youto != None:
                youto="<div class='order_use'>" + h.s_use_youto + "</div>"

            # 担当者
            tantou=Member.objects.get(tantou_id=h.tantou_id).tantou

            # その他
            com=h.com or ""
            name=(h.sei or "")+(h.mei or "")
            nouki=h.s_nouki or ""
            tel_last=h.tel_last_day or ""
            mail_last=h.mail_last_day or ""
            money=f"{h.money:,}円"


            title_str="<div class='houjin_card'>" \
                + "<div style='font-weight: bold;'>" + com + "</div>" \
                + "<div style='font-weight: bold;'>" + name + "</div>" \
                + "<div class='flex3' style='align-items: center;'><div class='flex' style='font-size: 0.9em;'>" \
                + "<div style='width: 45px;'>" + order + "</div>" \
                + "<div style='width: 30px;'>" + keiro + "</div>" \
                + "<div style='width: 30px;'>" + use + "</div>" \
                + "<div style='width: 30px;'>" + youto + "</div></div>" \
                + "<div class='flex'><div style='width: 37px;' id='" + h.mitsu_id + "' name='sfa_list'>" \
                + "<button type='button' class='btn btn-outline-secondary btn-sm' style='border-radius: 50%;' data-bs-toggle='modal' data-bs-target='#modal_est'>" \
                + "<i class='bi bi-pencil-square'></i></button></div>" \
                + "<div style='width: 35px;' id='" + h.cus_id + "' name='crm_list'>" \
                + "<button type='button' class='btn btn-outline-success btn-sm' style='border-radius: 50%;'>" \
                + "<i class='bi bi-person-square'></i></button></div></div></div>" \
                + "<div style='font-size: 0.9em;'>" \
                + "<div class='flex'><div style='width: 100px;'>担当者：</div><div>" + tantou + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>見積作成日：</div><div>" + h.make_day + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>見積番号：</div>" \
                + "<div><a href='" + h.mitsu_url + "' target='_blank'><span style='color: #008b8b;'><i class='bi bi-box-arrow-up-right'></i></span></a> " + h.mitsu_num + "-" + str(h.mitsu_ver) + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>確度：</div><div>" + h.kakudo + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>ステータス：</div><div>" + h.status + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>金額：</div><div>" + money + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>納期：</div><div>" + nouki + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>最終TEL：</div><div>" + tel_last + "</div></div>" \
                + "<div class='flex'><div style='width: 100px;'>最終メール：</div><div>" + mail_last + "</div></div>" \
                + "</div></div>"

            item.append({"id":h.mitsu_id,"title":title_str})

        dataContent.append({"id":"column_" + key,"title":val,"item":item})

    # dataContent=[
    #     {
    #         "id"    : "column_0",
    #         "title" : "新規取込",
    #         "item"  : [
    #         {
    #             "id"      : "cus_100",
    #             "title"   : "カード 1"
    #         },
    #         {
    #             "id"      : "cus_200",
    #             "title"   : "カード 2"
    #         }
    #         ],
    #         "class":"red",
    #     },
    #     {
    #         "id": "column_1",
    #         "title": "商談誘発",
    #         "item": [
    #         {
    #             "id": "cus_300",
    #             "title": "カード 3"
    #         }
    #         ],
    #         "class":"blue",
    #     },
    #     {
    #         "id": "column_2",
    #         "title": "見積・提案",
    #         "item": [
    #         {
    #             "id": "cus_400",
    #             "title": "カード 4<br><span style='font-size:1.5em; color:red;'>ddd</span>"
    #         }
    #         ],
    #         "class":"green",
    #     },

    #     ]

    d={"dataContent":dataContent}
    return JsonResponse(d)


# 法人案件ボード_移動
def houjin_move(request):
    column=request.POST.get("target_column")
    index_list=request.POST.get("col_index")
    column_num=column.replace("column_","")
    index_list=eval(index_list)

    for i,h in enumerate(index_list):
        ins=Sfa_data.objects.get(mitsu_id=h)
        ins.houjin_col=column_num
        ins.houjin_index=i
        ins.save()

    d={}
    return JsonResponse(d)


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

    params={
        "calendar_body":str_mon,
        "hassou_month":mon,
        "tantou_list":tantou_list,
        "tantou_id":tantou_id,
        }
    return render(request,"houjin/tantou_calendar.html",params)


# 法人外商リスト_取込
def houjin_gaishou_imp(request):
    data = io.TextIOWrapper(request.FILES['csv3'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    h=0
    for i in csv_list:
        if h!=0:
              Houjin_gaishou.objects.create(
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

    return render(request,"apr/approach_list.html",{"ans3":"yes"})


# 法人外商ボード_index
def houjin_gaishou_index(request):
    if "houjin_gaishou" not in request.session:
        request.session["houjin_gaishou"]={}
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

    ses=request.session["houjin_gaishou"]
    tantou_list=Member.objects.filter(houjin=1)
    itaku_result=["","アポ","資料送付","お断り","その他"]
    kubun_list=list(Houjin_gaishou.objects.all().values_list("kubun",flat=True).order_by("kubun").distinct())
    params={
        "tantou_list":tantou_list,
        "itaku_result":itaku_result,
        "kubun_list":kubun_list,
        "ses":ses,
    }
    return render(request,"houjin/gaishou.html",params)


# 法人外商ボード_load
def houjin_gaishou_load(request):
    col_name={
        "0":"新規",
        "1":"資料送付",
        "2":"アポ",
        "3":"失注",
        "4":"案件化",
        }
    
    # フィルター
    ses=request.session["houjin_gaishou"]
    fil={}
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
        fil["recieve_day__gte"]=ses["day_st"] + " 00:00"
    if ses["day_ed"] != "":
        fil["recieve_day__lte"]=ses["day_ed"] + " 23:59"
    
    dataContent=[]
    for key,val in col_name.items():
        fil["boad_col"]=key

        ins=Houjin_gaishou.objects.filter(**fil).order_by("boad_row")
        item=[]
        for h in ins:
            # 担当者
            tantou_dic={
                        "26":"mashimo.png",
                        "798":"kanayama.png",
                        "8":"mutou.png",
                        "43":"tanaka.png"
                        }
            if h.tantou_id != None and h.tantou_id != "":
                tantou_img="<img src='/static/" + tantou_dic[h.tantou_id] + "'>"
                tantou_name=h.tantou
            else:
                tantou_img=""
                tantou_name=""

            if h.last_update != None and h.last_update != "":
                last_update=h.last_update
            else:
                last_update=""

            if h.bikou != None and h.bikou != "":
                bikou=h.bikou
            else:
                bikou=""
                

            title_str="<div class='houjin_card'>" \
                + "<div class='flex'>" \
                    + "<div style='width: 70px;'>" + tantou_img + "</div>" \
                    + "<div style='font-size: 0.9em;'>" \
                        + "<div>受信：" + h.recieve_day + "</div>" \
                        + "<div>委託：" + h.kubun + "</div>" \
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
                            + "<div style='width: 60px;'>更新日：</div>" \
                            + "<div>" + last_update + "</div>" \
                        + "</div>" \
                        + "<div style='margin-top:5px'><textarea style='width: 100%; font-size: 0.8em;' rows='3' readonly>" + bikou + "</textarea>" \
                    + "</div>" \
                + "</div>" \
                + "</div>"

            item.append({"id":h.id,"title":title_str})

        dataContent.append({"id":"column_" + key,"title":val,"item":item})

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

    d={}
    return JsonResponse(d)


# 法人外商ボード_モーダル表示用
def houjin_gaishou_detail(request):
    gaishou_id=request.POST.get("gaishou_id")
    ins=list(Houjin_gaishou.objects.filter(id=gaishou_id).values())[0]
    d={"detail":ins}
    return JsonResponse(d)


# 法人外商ボード_保存
def houjin_gaishou_save(request):
    gaishou_id=request.POST.get("gaishou_id")
    tantou_id=request.POST.get("tantou_id")
    bikou=request.POST.get("bikou")
    itaku_result=request.POST.get("itaku_result")
    itaku_bikou=request.POST.get("itaku_bikou")

    ins=Houjin_gaishou.objects.get(id=gaishou_id)
    ins.tantou_id=tantou_id
    if tantou_id != "":
        ins.tantou=Member.objects.get(tantou_id=tantou_id).tantou
    else:
        ins.tantou=None
    ins.bikou=bikou
    ins.itaku_result=itaku_result
    ins.itaku_bikou=itaku_bikou
    ins.last_update=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ins.save()

    d={}
    return JsonResponse(d)


# 法人外商ボード_検索
def houjin_gaishou_search(request):
    request.session["houjin_gaishou"]["tantou"]=request.POST["tantou"]
    request.session["houjin_gaishou"]["kubun"]=request.POST["kubun"]
    request.session["houjin_gaishou"]["com"]=request.POST["com"]
    request.session["houjin_gaishou"]["name"]=request.POST["name"]
    request.session["houjin_gaishou"]["tel"]=request.POST["tel"]
    request.session["houjin_gaishou"]["mail"]=request.POST["mail"]
    request.session["houjin_gaishou"]["day_st"]=request.POST["day_st"]
    request.session["houjin_gaishou"]["day_ed"]=request.POST["day_ed"]
    return redirect("houjin:houjin_gaishou_index")


# 法人外商ボード_CSV出力
def houjin_gaishou_csv(request):
    day_st=request.POST["csv_day_st"]
    day_ed=request.POST["csv_day_ed"]

    ins=Houjin_gaishou.objects.filter(recieve_day__gte= day_st + " 00:00", recieve_day__lte= day_ed + " 23:59")
    recieve_list=[["日付","会社名","内容","メモ"]]
    for i in ins:
        recieve_list.append([datetime.date.today().strftime("%Y-%m-%d"),i.houjin_com,i.itaku_result,i.itaku_bikou])

    filename=urllib.parse.quote("カイタク報告用.csv")
    response = HttpResponse(content_type='text/csv; charset=CP932')
    response['Content-Disposition'] =  "attachment;  filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    writer = csv.writer(response)
    for line in recieve_list:
        writer.writerow(line)

    return response