from django.urls import path
from .views import index,kokyaku_detail_api


app_name="sfa"
urlpatterns = [
    path('', index, name="index"),
    path('kokyaku_detail_api/', kokyaku_detail_api, name="kokyaku_detail_api"),
]