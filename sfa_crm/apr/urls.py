from django.urls import path
from .views import approach_index,approach_search,approach_click,approach_title,approach_busho,approach_list_index,approach_list_add


app_name="apr"
urlpatterns = [
    path('approach_index/', approach_index, name="approach_index"),
    path('approach_search/', approach_search, name="approach_search"),
    path('approach_click/', approach_click, name="approach_click"),
    path('approach_title/', approach_title, name="approach_title"),
    path('approach_busho/', approach_busho, name="approach_busho"),
    path('approach_list_index/', approach_list_index, name="approach_list_index"),
    path('approach_list_add/', approach_list_add, name="approach_list_add"),
]