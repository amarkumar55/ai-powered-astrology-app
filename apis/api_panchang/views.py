from rest_framework import generics, permissions
from panchang.models import Panchang, UserPanchang
from .serializers import PanchangSerializer, UserPanchangSerializer
from rest_framework.pagination import PageNumberPagination

class PanchangListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class UserPanchangListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class PanchangListView(generics.ListAPIView):
    queryset = Panchang.objects.all().order_by('-date')
    serializer_class = PanchangSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PanchangListPagination

class PanchangDetailView(generics.RetrieveAPIView):
    queryset = Panchang.objects.all()
    serializer_class = PanchangSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]

class UserPanchangListView(generics.ListAPIView):
    queryset = UserPanchang.objects.all().order_by('-created_at')
    serializer_class = UserPanchangSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserPanchangListPagination

class UserPanchangDetailView(generics.RetrieveAPIView):
    queryset = UserPanchang.objects.all()
    serializer_class = UserPanchangSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 