from django.urls import path
from .views import DashaAntarDashaView

urlpatterns = [
    path("index", DashaAntarDashaView.as_view(), name="dasha.index"),  # ✅ Correct usage
]
