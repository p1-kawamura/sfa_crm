from django.contrib import admin
from .models import Crm_action,Customer
from django.contrib.admin import ModelAdmin


class A_Crm_action(ModelAdmin):
    model=Crm_action
    list_display=["act_id","cus_id","day","type","text"]


class A_Customer(ModelAdmin):
    model=Customer
    list_display=["cus_id","grip_busho_id","grip_tantou_id","mw"]

admin.site.register(Crm_action,A_Crm_action)
admin.site.register(Customer,A_Customer)