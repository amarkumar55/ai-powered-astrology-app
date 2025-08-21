from rest_framework import generics, permissions
from kundli.models import KundliReport
from .serializers import KundliReportSerializer
from rest_framework.pagination import PageNumberPagination

class KundliReportListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class KundliReportListView(generics.ListAPIView):
    queryset = KundliReport.objects.all().order_by('-created_at')
    serializer_class = KundliReportSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = KundliReportListPagination

class KundliReportDetailView(generics.RetrieveAPIView):
    queryset = KundliReport.objects.all()
    serializer_class = KundliReportSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 