from django.shortcuts import render,redirect
from sfa.models import Sfa_data,Member
from django.http import JsonResponse


def houjin_index(request):
    col_name=["新規取込","商談誘発","見積・提案","納期・価格交渉","確定・入稿待ち","イメージ・校正","受注","納品","失注","保留","リサイクル"]
    return render(request,"houjin/houjin_index.html",{"col_name":col_name})


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
                + "<div class='flex'><div style='width: 35px;' id='" + h.mitsu_id + "' name='sfa_list'>" \
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