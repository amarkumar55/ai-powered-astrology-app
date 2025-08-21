from django.urls import path
from .views import LoshuGridPredictionAPIView

urlpatterns = [
    path('predict/', LoshuGridPredictionAPIView.as_view(), name='api_loshugrid_predict'),
] 