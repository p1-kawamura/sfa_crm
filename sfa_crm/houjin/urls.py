from django.urls import path
from .views import houjin_index,houjin_load


app_name="houjin"
urlpatterns = [
    path('houjin_index/', houjin_index, name="houjin_index"),
    path('houjin_load/', houjin_load, name="houjin_load"),
]