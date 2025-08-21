from django.urls import path
from .views import (
    PanchangListView, PanchangDetailView,
    UserPanchangListView, UserPanchangDetailView
)

urlpatterns = [
    path('general/', PanchangListView.as_view(), name='api_panchang_list'),
    path('general/<int:id>/', PanchangDetailView.as_view(), name='api_panchang_detail'),
    path('user/', UserPanchangListView.as_view(), name='api_user_panchang_list'),
    path('user/<int:id>/', UserPanchangDetailView.as_view(), name='api_user_panchang_detail'),
] 