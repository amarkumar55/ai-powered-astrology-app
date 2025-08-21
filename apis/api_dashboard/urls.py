from django.urls import path
from .views import UserProfileListView, UserProfileDetailView,FeedView, TrendingNotesView


urlpatterns = [
    path('', UserProfileListView.as_view(), name='api_dashboard_user_list'),
    path('<int:id>/', UserProfileDetailView.as_view(), name='api_dashboard_user_detail'),
    path('feed/', FeedView.as_view(), name='feed'),
    path('trending/', TrendingNotesView.as_view(), name='trending-notes'),
] 