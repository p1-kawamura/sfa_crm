from django.urls import path
from .views import approach_index,approach_search,approach_click,approach_send,approach_busho_up,approach_busho_now,approach_list_index,approach_list_add,\
                    hangire_index,hangire_search,hangire_click,hangire_send,hangire_csv_imp,hangire_busho_up,hangire_busho_now ,\
                    han_list_page_prev,han_list_page_first,han_list_page_next,han_list_page_last


app_name="apr"
urlpatterns = [
    path('approach_index/', approach_index, name="approach_index"),
    path('approach_search/', approach_search, name="approach_search"),
    path('approach_click/', approach_click, name="approach_click"),
    path('approach_send/', approach_send, name="approach_send"),
    path('approach_busho_up/', approach_busho_up, name="approach_busho_up"),
    path('approach_busho_now/', approach_busho_now, name="approach_busho_now"),
    path('approach_list_index/', approach_list_index, name="approach_list_index"),
    path('approach_list_add/', approach_list_add, name="approach_list_add"),
    path('hangire_index/', hangire_index, name="hangire_index"),
    path('hangire_search/', hangire_search, name="hangire_search"),
    path('hangire_click/', hangire_click, name="hangire_click"),
    path('hangire_send/', hangire_send, name="hangire_send"),
    path('hangire_csv_imp/', hangire_csv_imp, name="hangire_csv_imp"),
    path('hangire_busho_up/', hangire_busho_up, name="hangire_busho_up"),
    path('hangire_busho_now/', hangire_busho_now, name="hangire_busho_now"),
    path('han_list_page_prev/', han_list_page_prev, name="han_list_page_prev"),
    path('han_list_page_first/', han_list_page_first, name="han_list_page_first"),
    path('han_list_page_next/', han_list_page_next, name="han_list_page_next"),
    path('han_list_page_last/', han_list_page_last, name="han_list_page_last"),
]