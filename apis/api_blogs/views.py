from rest_framework import generics, permissions
from blogs.models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.pagination import PageNumberPagination

class BlogListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class BlogListView(generics.ListAPIView):
    queryset = BlogPost.objects.filter(status='published').order_by('-published_at')
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = BlogListPagination

class BlogDetailView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny] 