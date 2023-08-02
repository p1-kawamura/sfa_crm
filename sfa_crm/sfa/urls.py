from django.urls import path
from .views import index,mitsu_detail_api,modal_top,modal_bot,modal_alert_check,kokyaku_detail_api,csv_imp


app_name="sfa"
urlpatterns = [
    path('', index, name="index"),
    path('mitsu_detail_api/', mitsu_detail_api, name="mitsu_detail_api"),
    path('modal_top/', modal_top, name="modal_top"),
    path('modal_bot/', modal_bot, name="modal_bot"),
    path('modal_alert_check/', modal_alert_check, name="modal_alert_check"),
    path('kokyaku_detail_api/', kokyaku_detail_api, name="kokyaku_detail_api"),
    path('csv_imp/', csv_imp, name="csv_imp"),
]