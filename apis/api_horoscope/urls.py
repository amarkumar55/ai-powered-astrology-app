from django.urls import path
from .views import HoroscopeListView, HoroscopeDetailView

urlpatterns = [
    path('', HoroscopeListView.as_view(), name='api_horoscope_list'),
    path('<int:id>/', HoroscopeDetailView.as_view(), name='api_horoscope_detail'),
]
