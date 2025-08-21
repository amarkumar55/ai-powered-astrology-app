from rest_framework import generics, permissions
from horoscope.models import Horoscope
from .serializers import HoroscopeSerializer
from rest_framework.pagination import PageNumberPagination

class HoroscopeListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class HoroscopeListView(generics.ListAPIView):
    queryset = Horoscope.objects.all().order_by('-date')
    serializer_class = HoroscopeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HoroscopeListPagination

class HoroscopeDetailView(generics.RetrieveAPIView):
    queryset = Horoscope.objects.all()
    serializer_class = HoroscopeSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 