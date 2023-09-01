from django.urls import path
from .views import index,search,busho_tantou,mitsu_detail_api,modal_top,modal_bot,modal_alert_check,kokyaku_detail_api,csv_imp,csv_imp_page, \
                    show_index,show,show_search,show_direct,show_settei,clear_sfa_data,clear_member,mw_page,mw_delete,mw_make,mw_download



app_name="sfa"
urlpatterns = [
    path('', index, name="index"),
    path('search/', search, name="search"),
    path('busho_tantou/', busho_tantou, name="busho_tantou"),
    path('mitsu_detail_api/', mitsu_detail_api, name="mitsu_detail_api"),
    path('modal_top/', modal_top, name="modal_top"),
    path('modal_bot/', modal_bot, name="modal_bot"),
    path('modal_alert_check/', modal_alert_check, name="modal_alert_check"),
    path('kokyaku_detail_api/', kokyaku_detail_api, name="kokyaku_detail_api"),
    path('show_index/', show_index, name="show_index"),
    path('show_search/', show_search, name="show_search"),
    path('show_direct/', show_direct, name="show_direct"),
    path('show_settei/', show_settei, name="show_settei"),
    path('show/', show, name="show"),
    path('mw_page/', mw_page, name="mw_page"),
    path('mw_delete/<int:pk>/', mw_delete, name="mw_delete"),
    path('mw_make/', mw_make, name="mw_make"),
    path('mw_download/', mw_download, name="mw_download"),
    path('csv_imp/', csv_imp, name="csv_imp"),
    path('csv_imp_page/', csv_imp_page, name="csv_imp_page"),
    path('clear_sfa_data/', clear_sfa_data, name="clear_sfa_data"),
    path('clear_member/', clear_member, name="clear_member"),
]