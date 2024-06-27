from django.urls import path
from .views import approach_index,approach_search,approach_click,approach_send,approach_title,approach_list_index,approach_list_add,\
                    hangire_index,hangire_csv_imp


app_name="apr"
urlpatterns = [
    path('approach_index/', approach_index, name="approach_index"),
    path('approach_search/', approach_search, name="approach_search"),
    path('approach_click/', approach_click, name="approach_click"),
    path('approach_send/', approach_send, name="approach_send"),
    path('approach_title/', approach_title, name="approach_title"),
    path('approach_list_index/', approach_list_index, name="approach_list_index"),
    path('approach_list_add/', approach_list_add, name="approach_list_add"),
    path('hangire_index/', hangire_index, name="hangire_index"),
    path('hangire_csv_imp/', hangire_csv_imp, name="hangire_csv_imp"),
]