from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Testdata
import csv
import io


def index(request):
    return render(request,"sfa/index.html")


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
            Testdata.objects.update_or_create(
                mitsu_id=i[0],
                defaults={
                    "mitsu_id":i[0],
                    "mitsu_ver":i[1],
                    "status":i[2],
                    "order_kubun":i[3],
                    "use_kubun":i[4],
                    "use_youto":i[5],
                    "shukka_annai":i[6],
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
                }            
            )
        h+=1
    return render(request,"sfa/index.html")