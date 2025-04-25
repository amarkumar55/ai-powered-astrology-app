from . import views
from django.urls import path

urlpatterns = [
    path("driver-conductor-prediction/index", views.DriverConductorView.as_view(), name="numerology.driver_conductor.index"),
    path("name-number-prediction/index", views.NameNumberView.as_view(), name="numerology.name_number.index"),
    path("life-path-number-prediction/index", views.LifePathView.as_view(), name="numerology.life_path_number.index"),
    path("destiny-path-number-prediction/index", views.DestinyPathView.as_view(), name="numerology.destiny_number.index"),
    path("personality-number-prediction/index", views.PersonalityNumberView.as_view(), name="numerology.personality_number.index"),
    path("personal-angel-number-prediction/index", views.AngelNumberView.as_view(), name="numerology.angel_number.index"),
]
