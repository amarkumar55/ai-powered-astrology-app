from . import views
from django.urls import path

urlpatterns = [
    path("daily-panchang-predition/index", views.PanchangListView.as_view(), name="panchang.index"),
    path("personalized-panchange-predition/index", views.UserPersonalizedPanchang.as_view(), name="panchang.user_personalized_panchang")
]