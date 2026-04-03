from django.shortcuts import render

def mkt_index(request):
    return render(request,"mkt/mkt_index.html")
