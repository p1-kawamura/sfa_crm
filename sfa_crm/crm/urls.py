from django.urls import path
from .views import index,kokyaku_api,crm_sort,crm_group_act,alert_check,list_click_est,list_click_act,list_add,list_del,grip_add,crm_bikou, \
                    mw_page,mw_add,mw_delete,mw_make,mw_download,cus_list_index,cus_list_busho,cus_list_search,cus_list_page_prev,cus_list_page_first,\
                    cus_list_page_next,cus_list_page_last,group_index,group_add_child,group_del_child,group_add_parent,group_del_all,group_cus_submit
                    

app_name="crm"
urlpatterns = [
    path('', index, name="index"),
    path('kokyaku_api/', kokyaku_api, name="kokyaku_api"),
    path('crm_sort/', crm_sort, name="crm_sort"),
    path('crm_group_act/', crm_group_act, name="crm_group_act"),
    path('alert_check/', alert_check, name="alert_check"),
    path('list_click_est/', list_click_est, name="list_click_est"),
    path('list_click_act/', list_click_act, name="list_click_act"),
    path('list_add/', list_add, name="list_add"),
    path('list_del/', list_del, name="list_del"),
    path('grip_add/', grip_add, name="grip_add"),
    path('crm_bikou/', crm_bikou, name="crm_bikou"),
    path('mw_page/', mw_page, name="mw_page"),
    path('mw_add/', mw_add, name="mw_add"),
    path('mw_delete/<int:pk>', mw_delete, name="mw_delete"),
    path('mw_make/', mw_make, name="mw_make"),
    path('mw_download/', mw_download, name="mw_download"),
    path('cus_list_index/', cus_list_index, name="cus_list_index"),
    path('cus_list_busho/', cus_list_busho, name="cus_list_busho"),
    path('cus_list_search/', cus_list_search, name="cus_list_search"),
    path('cus_list_page_prev/', cus_list_page_prev, name="cus_list_page_prev"),
    path('cus_list_page_first/', cus_list_page_first, name="cus_list_page_first"),
    path('cus_list_page_next/', cus_list_page_next, name="cus_list_page_next"),
    path('cus_list_page_last/', cus_list_page_last, name="cus_list_page_last"),
    path('group_index/', group_index, name="group_index"),
    path('group_del_all/', group_del_all, name="group_del_all"),
    path('group_add_child/', group_add_child, name="group_add_child"),
    path('group_del_child/', group_del_child, name="group_del_child"),
    path('group_add_parent/', group_add_parent, name="group_add_parent"),
    path('group_cus_submit/', group_cus_submit, name="group_cus_submit"),
]