from django.urls import path
from .views import index,kokyaku_api,list_click_est,list_click_act,list_add,list_del


app_name="crm"
urlpatterns = [
    path('', index, name="index"),
    path('kokyaku_api/', kokyaku_api, name="kokyaku_api"),
    path('list_click_est/', list_click_est, name="list_click_est"),
    path('list_click_act/', list_click_act, name="list_click_act"),
    path('list_add/', list_add, name="list_add"),
    path('list_del/', list_del, name="list_del"),
]