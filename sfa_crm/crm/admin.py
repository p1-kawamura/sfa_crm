from django.contrib import admin
from .models import Action
from django.contrib.admin import ModelAdmin


class A_Action(ModelAdmin):
    model=Action
    list_display=["action_id","cus_id","day","type","text"]

admin.site.register(Action,A_Action)