from django.urls import path
from .views import KundliMatchingListView, KundliMatchingDetailView

urlpatterns = [
    path('', KundliMatchingListView.as_view(), name='api_compatibility_list'),
    path('<int:id>/', KundliMatchingDetailView.as_view(), name='api_compatibility_detail'),
] 