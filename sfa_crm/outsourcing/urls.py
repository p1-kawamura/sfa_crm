from django.urls import path
from .views import outsourcing_index,outsourcing_list_add


app_name="outsourcing"
urlpatterns = [
    path('', outsourcing_index, name="outsourcing_index"),
    path('outsourcing_list_add', outsourcing_list_add, name="outsourcing_list_add"),
]