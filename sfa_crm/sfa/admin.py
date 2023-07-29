from django.contrib import admin
from .models import Testdata,Sfa_action
from django.contrib.admin import ModelAdmin


class A_Testdata(ModelAdmin):
    model=Testdata
    list_display=["mitsu_id","cus_id"]

admin.site.register(Testdata,A_Testdata)


class A_Sfa_action(ModelAdmin):
    model=Sfa_action
    list_display=["mitsu_id","day","type","tel_result","text"]

admin.site.register(Sfa_action,A_Sfa_action)