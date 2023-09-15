from django.contrib import admin
from .models import Crm_action,Grip,Customer
from django.contrib.admin import ModelAdmin


class A_Crm_action(ModelAdmin):
    model=Crm_action
    list_display=["act_id","cus_id","day","type","text"]

class A_Grip(ModelAdmin):
    model=Grip
    list_display=["cus_id","busho_id","tantou_id"]

class A_Customer(ModelAdmin):
    model=Customer
    list_display=["cus_id","busho_id","tantou_id","mw"]

admin.site.register(Crm_action,A_Crm_action)
admin.site.register(Grip,A_Grip)
admin.site.register(Customer,A_Customer)