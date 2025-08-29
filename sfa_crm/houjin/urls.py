from django.urls import path
from .views import houjin_index,houjin_load,houjin_move,calendar_index,houjin_gaishou_imp,houjin_gaishou_index,houjin_gaishou_load,\
                    houjin_gaishou_move,houjin_gaishou_detail,houjin_gaishou_save


app_name="houjin"
urlpatterns = [
    path('houjin_index/', houjin_index, name="houjin_index"),
    path('houjin_load/', houjin_load, name="houjin_load"),
    path('houjin_move/', houjin_move, name="houjin_move"),
    path('calendar_index/', calendar_index, name="calendar_index"),
    path('houjin_gaishou_imp/', houjin_gaishou_imp, name="houjin_gaishou_imp"),
    path('houjin_gaishou_index/', houjin_gaishou_index, name="houjin_gaishou_index"),
    path('houjin_gaishou_load/', houjin_gaishou_load, name="houjin_gaishou_load"),
    path('houjin_gaishou_move/', houjin_gaishou_move, name="houjin_gaishou_move"),
    path('houjin_gaishou_detail/', houjin_gaishou_detail, name="houjin_gaishou_detail"),
    path('houjin_gaishou_save/', houjin_gaishou_save, name="houjin_gaishou_save"),
]