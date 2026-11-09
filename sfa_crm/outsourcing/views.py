from django.shortcuts import render,redirect
from .models import Outsourcing,Outsourcing_list
from crm.models import Customer
from apr.models import Approach_list
import requests
from datetime import date
import csv
import io
from django_pandas.io import read_frame
import pandas as pd



def outsourcing_index(request):
    return render(request,"outsourcing/outsourcing_index.html")


# 外注アプローチリスト設定_追加
def outsourcing_list_add(request):
    approach_id=request.POST["approach_id"]
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


