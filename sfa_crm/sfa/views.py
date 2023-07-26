from django.shortcuts import render,redirect
from django.http import JsonResponse


def index(request):
    return render(request,"sfa/index.html")


def kokyaku_detail_api(request):
    cus_id=request.POST.get("cus_id")
    request.session["cus_id"]=cus_id
    d={}
    return JsonResponse(d)
