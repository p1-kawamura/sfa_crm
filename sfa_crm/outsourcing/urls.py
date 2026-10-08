from django.urls import path
from .views import outsourcing_index


app_name="outsourcing"
urlpatterns = [
    path('', outsourcing_index, name="outsourcing_index"),
]