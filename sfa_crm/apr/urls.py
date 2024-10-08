from django.urls import path
from .views import approach_list_index,approach_list_add,\
                    hangire_index,hangire_search,hangire_modal_send,hangire_csv_imp,hangire_busho_up,hangire_busho_now,hangire_modal_show_top,\
                    hangire_modal_show_bot,hangire_modal_sort,hangire_modal_list_click,hangire_modal_btn,hangire_modal_del,hangire_modal_result_del,\
                    hangire_modal_result_juchu,hangire_color_clear,choice_id,\
                    han_list_page_prev,han_list_page_first,han_list_page_next,han_list_page_last,\
                    shukei_index,shukei_click


app_name="apr"
urlpatterns = [
    path('approach_list_index/', approach_list_index, name="approach_list_index"),
    path('approach_list_add/', approach_list_add, name="approach_list_add"),
    path('hangire_index/', hangire_index, name="hangire_index"),
    path('hangire_search/', hangire_search, name="hangire_search"),
    path('hangire_modal_show_top/', hangire_modal_show_top, name="hangire_modal_show_top"),
    path('hangire_modal_show_bot/', hangire_modal_show_bot, name="hangire_modal_show_bot"),
    path('hangire_modal_sort/', hangire_modal_sort, name="hangire_modal_sort"),
    path('hangire_modal_list_click/', hangire_modal_list_click, name="hangire_modal_list_click"),
    path('hangire_modal_btn/', hangire_modal_btn, name="hangire_modal_btn"),
    path('hangire_modal_del/', hangire_modal_del, name="hangire_modal_del"),
    path('hangire_modal_result_del/', hangire_modal_result_del, name="hangire_modal_result_del"),
    path('hangire_modal_result_juchu/', hangire_modal_result_juchu, name="hangire_modal_result_juchu"),
    path('hangire_modal_send/', hangire_modal_send, name="hangire_modal_send"),
    path('hangire_color_clear/', hangire_color_clear, name="hangire_color_clear"),
    path('hangire_csv_imp/', hangire_csv_imp, name="hangire_csv_imp"),
    path('hangire_busho_up/', hangire_busho_up, name="hangire_busho_up"),
    path('hangire_busho_now/', hangire_busho_now, name="hangire_busho_now"),
    path('choice_id/', choice_id, name="choice_id"),
    path('han_list_page_prev/', han_list_page_prev, name="han_list_page_prev"),
    path('han_list_page_first/', han_list_page_first, name="han_list_page_first"),
    path('han_list_page_next/', han_list_page_next, name="han_list_page_next"),
    path('han_list_page_last/', han_list_page_last, name="han_list_page_last"),
    path('shukei_index/', shukei_index, name="shukei_index"),
    path('shukei_click/', shukei_click, name="shukei_click"),
]