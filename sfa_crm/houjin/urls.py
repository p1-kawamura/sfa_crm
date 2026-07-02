from django.urls import path
from .views import calendar_index,houjin_gaishou_imp,houjin_gaishou_index,houjin_gaishou_load,\
                    houjin_gaishou_move,houjin_gaishou_detail,houjin_gaishou_save,houjin_gaishou_search,houjin_gaishou_xlsx,\
                    houjin_gaishou_search_dl,houjin_gaishou_busho,next_action_index


app_name="houjin"
urlpatterns = [
    path('calendar_index/', calendar_index, name="calendar_index"),
    path('houjin_gaishou_imp/', houjin_gaishou_imp, name="houjin_gaishou_imp"),
    path('houjin_gaishou_index/', houjin_gaishou_index, name="houjin_gaishou_index"),
    path('houjin_gaishou_load/', houjin_gaishou_load, name="houjin_gaishou_load"),
    path('houjin_gaishou_move/', houjin_gaishou_move, name="houjin_gaishou_move"),
    path('houjin_gaishou_detail/', houjin_gaishou_detail, name="houjin_gaishou_detail"),
    path('houjin_gaishou_save/', houjin_gaishou_save, name="houjin_gaishou_save"),
    path('houjin_gaishou_search/', houjin_gaishou_search, name="houjin_gaishou_search"),
    path('houjin_gaishou_xlsx/', houjin_gaishou_xlsx, name="houjin_gaishou_xlsx"),
    path('houjin_gaishou_search_dl/', houjin_gaishou_search_dl, name="houjin_gaishou_search_dl"),
    path('houjin_gaishou_busho/', houjin_gaishou_busho, name="houjin_gaishou_busho"),
    path('next_action_index/', next_action_index, name="next_action_index"),
]