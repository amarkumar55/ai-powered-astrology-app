from django.urls import path
from .views import CompatibilityView

urlpatterns = [
    path("index", CompatibilityView.as_view(), name="matching.index")
]