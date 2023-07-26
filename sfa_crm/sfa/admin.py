from django.contrib import admin
from .models import Testdata
from django.contrib.admin import ModelAdmin


class A_Testdata(ModelAdmin):
    model=Testdata
    list_display=["mitsu_id","cus_id"]

admin.site.register(Testdata,A_Testdata)