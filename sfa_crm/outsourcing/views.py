from django.shortcuts import render,redirect
from .models import Outsourcing,Outsourcing_list
from sfa.models import Member
from crm.models import Customer
from apr.models import Approach_list
import requests
from django.http import JsonResponse,HttpResponse
from datetime import date
import json
import csv
import io
from django_pandas.io import read_frame
import pandas as pd
from io import BytesIO
import urllib.parse



# 外注アプローチリスト設定_追加
def outsourcing_list_add(request):
    approach_id=request.POST["approach_id"]
    if "out_" not in approach_id:
        approach_id="out_" + approach_id
    title=request.POST["title"]
    day=request.POST["day"]
    day_type=request.POST["day_type"]

    # CSV取込
    data = io.TextIOWrapper(request.FILES['csv5'].file, encoding="cp932")
    csv_content = csv.reader(data)
    csv_list=list(csv_content)

    # Outsourcing_list
    Outsourcing_list.objects.create(approach_id=approach_id,title=title,day=day,day_type=day_type)

    h=0
    for i in csv_list:
        if h!=0:
            try:
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

                # Outsourcing
                Outsourcing.objects.create(
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
                print(h)

            except:
                print("error："+ str(h))

        h+=1
    ins=Approach_list.objects.all()
    ins2=Outsourcing_list.objects.all()
    return render(request,"apr/approach_list.html",{"ans5":"yes","list":ins,"list2":ins2})



def outsourcing_index(request):
    if "out_search" not in request.session:
        request.session["out_search"]={}
    if "out_kinyu" not in request.session["out_search"]:
        request.session["out_search"]["out_kinyu"]=""
    if "out_busho" not in request.session["out_search"]:
        request.session["out_search"]["out_busho"]=""
    if "out_tantou" not in request.session["out_search"]:
        request.session["out_search"]["out_tantou"]=""
    if "out_pref" not in request.session["out_search"]:
        request.session["out_search"]["out_pref"]=""
    if "out_com" not in request.session["out_search"]:
        request.session["out_search"]["out_com"]=""
    if "out_sei" not in request.session["out_search"]:
        request.session["out_search"]["out_sei"]=""
    if "out_mei" not in request.session["out_search"]:
        request.session["out_search"]["out_mei"]=""
    if "out_tel" not in request.session["out_search"]:
        request.session["out_search"]["out_tel"]=""
    if "out_result" not in request.session["out_search"]:
        request.session["out_search"]["out_result"]=[]
    if "out_day_st" not in request.session["out_search"]:
        request.session["out_search"]["out_day_st"]=""
    if "out_day_ed" not in request.session["out_search"]:
        request.session["out_search"]["out_day_ed"]=""
    if "page_num" not in request.session["out_search"]:
        request.session["out_search"]["page_num"]=1
    if "all_page_num" not in request.session["out_search"]:
        request.session["out_search"]["all_page_num"]=""
    if "sort_name" not in request.session["out_search"]:
        request.session["out_search"]["sort_name"]="juchu_day"
    if "sort_jun" not in request.session["out_search"]:
        request.session["out_search"]["sort_jun"]="0"  
    if "out_pk" not in request.session["out_search"]:
        request.session["out_search"]["out_pk"]="0"
    if "approach_id" not in request.session["out_search"]:
        request.session["out_search"]["approach_id"]=""

    ses=request.session["out_search"]
    
    # フィルター
    fil={}
    fil["approach_id"]=ses["approach_id"]
    approach_id=ses["approach_id"]
    if ses["out_kinyu"] != "":
            fil["apr_tantou"]=ses["out_kinyu"]
    if ses["out_busho"] != "":
        fil["busho_apr_id"]=ses["out_busho"]
    if ses["out_tantou"] != "":
        fil["tantou_apr_id"]=ses["out_tantou"]
    if ses["out_pref"] != "":
        fil["pref"]=ses["out_pref"]
    if ses["out_com"] != "":
        fil["cus_com__contains"]=ses["out_com"].strip()
    if ses["out_sei"] != "":
        fil["cus_sei__contains"]=ses["out_sei"].strip()
    if ses["out_mei"] != "":
        fil["cus_mei__contains"]=ses["out_mei"].strip()
    if ses["out_day_st"] != "":
        fil["juchu_day__gte"]=ses["out_day_st"]
    if ses["out_day_ed"] != "":
        fil["juchu_day__lte"]=ses["out_day_ed"]

    if ses["out_tel"] != "":
        tel=ses["out_tel"].strip().replace("-","")
        ins_tel=list(Outsourcing.objects.filter(cus_tel_search=tel).values_list("cus_id",flat=True))
        ins_mob=list(Outsourcing.objects.filter(cus_mob_search=tel).values_list("cus_id",flat=True))
        list_tel_mob=set(ins_tel + ins_mob)
        fil["cus_id__in"]=list_tel_mob
    

    # 進捗を含めない個数
    ins=Outsourcing.objects.filter(**fil)
    result_list=[["0","未対応"],["1","アプローチしない"],["2","不在"],["3","検討します"],
                    ["4","失注/予定なし"],["5","架電により案件化"],["6","受注"],["7","その他"]]
    for i in result_list:
        i.append(ins.filter(result=i[0]).count())

    # 進捗を含む
    if len(ses["out_result"])!=0:
        fil["result__in"]=ses["out_result"]
    
    # 並び順
    if ses["sort_jun"]=="0":
        ins=Outsourcing.objects.filter(**fil).order_by(ses["sort_name"])
    else:
        ins=Outsourcing.objects.filter(**fil).order_by(ses["sort_name"]).reverse()
    
    
    result=ins.count()
    #全ページ数
    if result == 0:
        all_num = 1
    elif result % 100 == 0:
        all_num = result / 100
    else:
        all_num = result // 100 + 1
    all_num=int(all_num)
    request.session["out_search"]["all_page_num"]=all_num
    num=ses["page_num"]
    if all_num==1:
        num=1
        request.session["out_search"]["page_num"]=1
    ins=ins[(num-1)*100 : num*100]

    # 部署設定
    busho_list=list(Outsourcing.objects.filter(approach_id=approach_id).values_list("busho_id","busho_name").order_by("busho_id").distinct())

    # 担当設定
    busho_id=ses["out_busho"]
    
    if busho_id=="":
        tantou_list=list(Outsourcing.objects.all().values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
    else:
        tantou_list=list(Outsourcing.objects.filter(approach_id=approach_id,busho_id=busho_id).values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())

    # その他必要情報
    pk=request.session["out_search"]["out_pk"]
    apr_list=Outsourcing_list.objects.all()

    if ses["approach_id"]!="":
        if Outsourcing_list.objects.get(approach_id=ses["approach_id"]).day_type == 1:
            sort_name="見積日"
        else:
            sort_name="受注日"
    else:
        sort_name="受注日"
    

    # 集計
    ins2=Outsourcing.objects.filter(approach_id=approach_id)
    shu_dic={}
    if ins2.count()>0:
        cnt_list=[]
        for i in range(8):
            cnt_list.append(ins2.filter(result=str(i)).count())
        all_cnt=sum(cnt_list)-cnt_list[1]
        for i in range(8):
            shu_dic[str(i)]=[cnt_list[i],cnt_list[i]/all_cnt*100]
        shu_dic["8"]=[all_cnt-cnt_list[0],all_cnt,(all_cnt-cnt_list[0])/all_cnt*100]


    params={
        "cus_list":ins,
        "result_list":result_list,
        "apr_list":apr_list,
        "busho_list":busho_list,
        "tantou_list":tantou_list,
        "pref_list":[
            '','北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', 
            '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県' ,'岐阜県','静岡県','愛知県',
            '三重県','滋賀県', '京都府', '大阪府','兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', 
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'],
        "sort_name":sort_name,
        "ses":ses,
        "num":num,
        "all_num":all_num,
        "pk":int(pk),
        "shu_dic":shu_dic,
        }
    return render(request,"outsourcing/outsourcing_index.html",params)


# アプローチリスト選択
def out_id_choice(request):
    request.session["out_search"]["approach_id"]=request.POST.get("choice_outsourcing_id")
    return redirect("outsourcing:outsourcing_index")


# 部署選択
def out_busho(request):
    approach_id=request.session["out_search"]["approach_id"]
    busho_id=request.POST.get("busho_id")
    if busho_id=="":
        tantou_list=list(Outsourcing.objects.filter(approach_id=approach_id)
                         .values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
    else:
        tantou_list=list(Outsourcing.objects.filter(approach_id=approach_id,busho_id=busho_id)
                         .values_list("tantou_id","tantou_sei","tantou_mei").order_by("tantou_id").distinct())
    d={"tantou_list":tantou_list}
    return JsonResponse(d)


# 詳細検索
def out_search(request):
    request.session["out_search"]["out_kinyu"]=request.POST["out_kinyu"]
    request.session["out_search"]["out_busho"]=request.POST["out_busho"]
    request.session["out_search"]["out_tantou"]=request.POST["out_tantou"]
    request.session["out_search"]["out_pref"]=request.POST["out_pref"]
    request.session["out_search"]["out_com"]=request.POST["out_com"]
    request.session["out_search"]["out_sei"]=request.POST["out_sei"]
    request.session["out_search"]["out_mei"]=request.POST["out_mei"]
    request.session["out_search"]["out_tel"]=request.POST["out_tel"]
    request.session["out_search"]["out_day_st"]=request.POST["out_day_st"]
    request.session["out_search"]["out_day_ed"]=request.POST["out_day_ed"]
    request.session["out_search"]["out_result"]=request.POST.getlist("out_result")
    request.session["out_search"]["sort_jun"]=request.POST["sort_jun"]
    request.session["out_search"]["page_num"]=1
    return redirect("outsourcing:outsourcing_index")


# モーダル_内容取得
def out_modal_detail(request):
    pk=request.POST.get("pk").replace("open_","")
    cus_id=Outsourcing.objects.get(pk=pk).cus_id
    request.session["out_search"]["out_pk"]=pk
    result=list(Outsourcing.objects.filter(pk=pk).values())
    last_apr=Customer.objects.get(cus_id=cus_id).contact_last

    # 顧客マスタ備考
    url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id
    res=requests.get(url)
    res=res.json()

    d={"pk":pk,"result":result,"last_apr":last_apr,"bikou":res["remark"]} 
    return JsonResponse(d)


# モーダル_決定ボタン
def out_modal_btn(request):
    pk=request.POST.get("pk")
    result=request.POST.get("result")
    tantou=request.POST.get("tantou")
    day=request.POST.get("day")
    text=request.POST.get("text")
    bikou=request.POST.get("bikou")
    d={}
    try:
        # Outsourcingへ
        ins=Outsourcing.objects.get(pk=pk)
        ins.result=result
        ins.apr_day=day
        ins.apr_tantou=tantou
        ins.apr_text=text
        ins.save()

        # 新基幹の顧客備考
        cus_id=Outsourcing.objects.get(pk=pk).cus_id        
        data={"remark":bikou}
        data=json.dumps(data)
        url="https://core-sys.p1-intl.co.jp/p1web/v1/customers/" + cus_id + "/remark"
        requests.put(url,data=data)

        d["result"]="ok"

    except:
        d["result"]="no"
    
    return JsonResponse(d)


# 前回モーダル分カラークリア
def out_color_clear(request):
    request.session["out_search"]["out_pk"]="0"
    d={}
    return JsonResponse(d)


# ページネーション
def out_list_page_prev(request):
    num=request.session["out_search"]["page_num"]
    if num-1 > 0:
        request.session["out_search"]["page_num"] = num - 1
    return redirect("outsourcing:outsourcing_index")

def out_list_page_first(request):
    request.session["out_search"]["page_num"] = 1
    return redirect("outsourcing:outsourcing_index")

def out_list_page_next(request):
    num=request.session["out_search"]["page_num"]
    all_num=request.session["out_search"]["all_page_num"]
    if num+1 <= all_num:
        request.session["out_search"]["page_num"] = num + 1
    return redirect("outsourcing:outsourcing_index")

def out_list_page_last(request):
    all_num=request.session["out_search"]["all_page_num"]
    request.session["out_search"]["page_num"]=all_num
    return redirect("outsourcing:outsourcing_index")


# アプローチ結果DL
def out_download(request):
    approach_id=request.session["out_search"]["approach_id"]
    ins=Outsourcing.objects.filter(approach_id=approach_id)
    df=read_frame(ins)

    col_name={
        "0":"未対応",
        "1":"アプローチしない",
        "2":"不在",        
        "3":"検討します",
        "4":"失注/予定なし",
        "5":"架電により案件化",
        "6":"受注",
        "7":"その他",
        }
    df["result"]=df["result"].map(col_name)

    # 最終フォーマット
    df_dl=df[["result","apr_day","apr_tantou","apr_text","juchu_day","pref","cus_com","cus_sei","cus_mei"]]
    df_dl_col=["結果","日付","記入者","備考","受注日","都道府県","会社","姓","名"]
    df_dl.columns=df_dl_col

    # Excelファイルをメモリ上に作成
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_dl.to_excel(writer, index=False, sheet_name='アプローチ結果')
    buffer.seek(0)

    # HTTPレスポンスとしてExcelファイルを返す
    filename = urllib.parse.quote("アプローチ結果.xlsx")
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = (
        "attachment; filename='{}'; filename*=UTF-8''{}".format(filename, filename)
    )

    return response