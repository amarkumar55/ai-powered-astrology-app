from django.urls import path
from .views import BlogListView, BlogDetailView

urlpatterns = [
    path('', BlogListView.as_view(), name='api_blogs'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='api_blog_detail'),
] 