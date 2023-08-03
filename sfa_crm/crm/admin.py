from django.contrib import admin
from .models import Crm_action
from django.contrib.admin import ModelAdmin


class A_Crm_action(ModelAdmin):
    model=Crm_action
    list_display=["act_id","cus_id","day","type","text"]

admin.site.register(Crm_action,A_Crm_action)