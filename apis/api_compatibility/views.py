from rest_framework import generics, permissions
from compatibility.models import KundliMatching
from .serializers import KundliMatchingSerializer
from rest_framework.pagination import PageNumberPagination

class KundliMatchingListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class KundliMatchingListView(generics.ListAPIView):
    queryset = KundliMatching.objects.all().order_by('-created_at')
    serializer_class = KundliMatchingSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = KundliMatchingListPagination

class KundliMatchingDetailView(generics.RetrieveAPIView):
    queryset = KundliMatching.objects.all()
    serializer_class = KundliMatchingSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 