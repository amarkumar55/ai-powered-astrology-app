from django.urls import path
from .views import (
    AntarDashaListView, AntarDashaDetailView,
    DashaEffectListView, DashaEffectDetailView
)

urlpatterns = [
    path('antar-dasha/', AntarDashaListView.as_view(), name='api_antar_dasha_list'),
    path('antar-dasha/<int:id>/', AntarDashaDetailView.as_view(), name='api_antar_dasha_detail'),
    path('dasha-effect/', DashaEffectListView.as_view(), name='api_dasha_effect_list'),
    path('dasha-effect/<int:id>/', DashaEffectDetailView.as_view(), name='api_dasha_effect_detail'),
] 