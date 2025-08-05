from django.shortcuts import render,redirect
from sfa.models import Sfa_data
from django.http import JsonResponse


def houjin_index(request):
    return render(request,"houjin/houjin_index.html")


def houjin_load(request):
    dataContent=[
        {
            "id"    : "column_0",
            "title" : "新規取込",
            "item"  : [
            {
                "id"      : "cus_100",
                "title"   : "カード 1"
            },
            {
                "id"      : "cus_200",
                "title"   : "カード 2"
            }
            ],
            "class":"red",
        },
        {
            "id": "column_1",
            "title": "商談誘発",
            "item": [
            {
                "id": "cus_300",
                "title": "カード 3"
            }
            ],
            "class":"blue",
        },
        {
            "id": "column_2",
            "title": "見積・提案",
            "item": [
            {
                "id": "cus_400",
                "title": "カード 4<br><span style='font-size:1.5em; color:red;'>ddd</span>"
            }
            ],
            "class":"green",
        },
        {
            "id": "column_3",
            "title": "納期・価格交渉",
            "item": []
        },
        {
            "id": "column_4",
            "title": "確定・入稿待ち",
            "item": []
        },
        {
            "id": "column_5",
            "title": "イメージ・校正",
            "item": []
        },
        {
            "id": "column_6",
            "title": "受注",
            "item": []
        },
        {
            "id": "column_7",
            "title": "納品",
            "item": []
        },
        {
            "id": "column_8",
            "title": "失注",
            "item": []
        },
        {
            "id": "column_9",
            "title": "保留",
            "item": []
        },
        {
            "id": "column_10",
            "title": "リサイクル",
            "item":[]
        }
        ]

    d={"dataContent":dataContent}
    return JsonResponse(d)
