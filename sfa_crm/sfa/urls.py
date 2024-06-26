from django.urls import path
from .views import index_api,index,search,busho_tantou,mitsu_detail_api,modal_top,modal_bot,modal_bot_click,modal_bot_delete,modal_alert_check,kokyaku_detail_api, \
                    show_index,show,show_search,show_direct,show_settei,clear_session,mw_page,mw_add,mw_delete,mw_make,mw_download, \
                    mw_download_auto,show_list_direct,hidden_index,hidden_list_direct,kakudo_index,member_index,member_add,csv_imp,csv_imp_page,modal_group_click, \
                    sfa_page_prev,sfa_page_first,sfa_page_next,sfa_page_last,credit_url



app_name="sfa"
urlpatterns = [
    path('', index_api, name="index_api"),
    path('index/', index, name="index"),
    path('search/', search, name="search"),
    path('sfa_page_prev/', sfa_page_prev, name="sfa_page_prev"),
    path('sfa_page_first/', sfa_page_first, name="sfa_page_first"),
    path('sfa_page_next/', sfa_page_next, name="sfa_page_next"),
    path('sfa_page_last/', sfa_page_last, name="sfa_page_last"),
    path('busho_tantou/', busho_tantou, name="busho_tantou"),
    path('mitsu_detail_api/', mitsu_detail_api, name="mitsu_detail_api"),
    path('modal_top/', modal_top, name="modal_top"),
    path('modal_bot/', modal_bot, name="modal_bot"),
    path('modal_bot_click/', modal_bot_click, name="modal_bot_click"),
    path('modal_bot_delete/', modal_bot_delete, name="modal_bot_delete"),
    path('modal_alert_check/', modal_alert_check, name="modal_alert_check"),
    path('modal_group_click/', modal_group_click, name="modal_group_click"),
    path('kokyaku_detail_api/', kokyaku_detail_api, name="kokyaku_detail_api"),
    path('show_index/', show_index, name="show_index"),
    path('show_search/', show_search, name="show_search"),
    path('show_direct/', show_direct, name="show_direct"),
    path('show_settei/', show_settei, name="show_settei"),
    path('show/', show, name="show"),
    path('mw_page/', mw_page, name="mw_page"),
    path('mw_add/', mw_add, name="mw_add"),
    path('mw_delete/<int:pk>/', mw_delete, name="mw_delete"),
    path('mw_make/', mw_make, name="mw_make"),
    path('mw_download/', mw_download, name="mw_download"),
    path('mw_download_auto/', mw_download_auto, name="mw_download_auto"),
    path('show_list_direct/', show_list_direct, name="show_list_direct"),
    path('hidden_index/', hidden_index, name="hidden_index"),
    path('hidden_list_direct/', hidden_list_direct, name="hidden_list_direct"),
    path('kakudo_index/', kakudo_index, name="kakudo_index"),
    path('member_index/', member_index, name="member_index"),
    path('member_add/', member_add, name="member_add"),
    path('csv_imp/', csv_imp, name="csv_imp"),
    path('csv_imp_page/', csv_imp_page, name="csv_imp_page"),
    path('clear_session/', clear_session, name="clear_session"),
    path('credit_url/', credit_url, name="credit_url"),
]