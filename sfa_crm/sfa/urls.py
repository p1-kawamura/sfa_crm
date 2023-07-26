from django.urls import path
from .views import index,kokyaku_detail_api,csv_imp


app_name="sfa"
urlpatterns = [
    path('', index, name="index"),
    path('kokyaku_detail_api/', kokyaku_detail_api, name="kokyaku_detail_api"),
    path('csv_imp/', csv_imp, name="csv_imp"),
]