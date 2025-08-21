from django.urls import path
from .views import houjin_index,houjin_load,houjin_move,calendar_index


app_name="houjin"
urlpatterns = [
    path('houjin_index/', houjin_index, name="houjin_index"),
    path('houjin_load/', houjin_load, name="houjin_load"),
    path('houjin_move/', houjin_move, name="houjin_move"),
    path('calendar_index/', calendar_index, name="calendar_index"),
]