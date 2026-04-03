from django.urls import path
from .views import mkt_index


app_name="mkt"
urlpatterns = [
    path('mkt_index/', mkt_index, name="mkt_index"),
]