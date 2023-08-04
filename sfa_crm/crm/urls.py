from django.urls import path
from .views import index,kokyaku_api,alert_check,list_click_est,list_click_act,list_add,list_del,grip_index,grip_add


app_name="crm"
urlpatterns = [
    path('', index, name="index"),
    path('kokyaku_api/', kokyaku_api, name="kokyaku_api"),
    path('alert_check/', alert_check, name="alert_check"),
    path('list_click_est/', list_click_est, name="list_click_est"),
    path('list_click_act/', list_click_act, name="list_click_act"),
    path('list_add/', list_add, name="list_add"),
    path('list_del/', list_del, name="list_del"),
    path('grip_index/', grip_index, name="grip_index"),
    path('grip_add/', grip_add, name="grip_add"),
]