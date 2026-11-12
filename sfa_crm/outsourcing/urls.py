from django.urls import path
from .views import outsourcing_index,outsourcing_list_add,out_id_choice,out_busho,out_search,out_modal_detail,out_modal_btn,out_color_clear,out_download, \
    out_list_page_first,out_list_page_prev,out_list_page_next,out_list_page_last


app_name="outsourcing"
urlpatterns = [
    path('', outsourcing_index, name="outsourcing_index"),
    path('outsourcing_list_add', outsourcing_list_add, name="outsourcing_list_add"),
    path('out_id_choice', out_id_choice, name="out_id_choice"),
    path('out_busho', out_busho, name="out_busho"),
    path('out_search', out_search, name="out_search"),
    path('out_modal_detail', out_modal_detail, name="out_modal_detail"),
    path('out_modal_btn', out_modal_btn, name="out_modal_btn"),
    path('out_color_clear', out_color_clear, name="out_color_clear"),
    path('out_download', out_download, name="out_download"),
    path('out_list_page_first', out_list_page_first, name="out_list_page_first"),
    path('out_list_page_prev', out_list_page_prev, name="out_list_page_prev"),
    path('out_list_page_next', out_list_page_next, name="out_list_page_next"),
    path('out_list_page_last', out_list_page_last, name="out_list_page_last"),
]