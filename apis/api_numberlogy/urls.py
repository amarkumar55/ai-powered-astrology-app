from django.urls import path
from .views import (
    NameNumberAPIView, DriverConductorAPIView, LifePathNumberAPIView, DestinyNumberAPIView, PersonalityNumberAPIView
)

urlpatterns = [
    path('name-number/', NameNumberAPIView.as_view(), name='api_numberlogy_name_number'),
    path('driver-conductor/', DriverConductorAPIView.as_view(), name='api_numberlogy_driver_conductor'),
    path('life-path/', LifePathNumberAPIView.as_view(), name='api_numberlogy_life_path'),
    path('destiny/', DestinyNumberAPIView.as_view(), name='api_numberlogy_destiny'),
    path('personality/', PersonalityNumberAPIView.as_view(), name='api_numberlogy_personality'),
] 