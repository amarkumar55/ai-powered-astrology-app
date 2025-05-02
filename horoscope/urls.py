from . import views
from django.urls import path

urlpatterns = [
    path("personalized-horoscope/index", views.user_horoscope, name="horoscope.index"),
    path('horoscope/daily/', views.daily_horoscope, name='horoscope.daily_horoscope'),
    path('horoscope/weekly/', views.weekly_horoscope, name='horoscope.weekly_horoscope'),
]