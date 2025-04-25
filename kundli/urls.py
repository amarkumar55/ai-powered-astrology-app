from . import views
from django.urls import path

urlpatterns = [
   path("index", views.KundliPreditionView.as_view(), name="kundli.index"),
   path("search-location", views.SearchLocationView.as_view(), name="search_location"),
]
