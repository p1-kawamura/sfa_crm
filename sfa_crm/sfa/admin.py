from django.contrib import admin
from .models import Sfa_data,Sfa_action
from django.contrib.admin import ModelAdmin


class A_Sfa_data(ModelAdmin):
    model=Sfa_data
    list_display=["mitsu_id","cus_id"]

admin.site.register(Sfa_data,A_Sfa_data)


class A_Sfa_action(ModelAdmin):
    model=Sfa_action
    list_display=["act_id","mitsu_id","day","type","tel_result","text","alert_check"]

admin.site.register(Sfa_action,A_Sfa_action)