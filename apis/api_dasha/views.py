from rest_framework import generics, permissions
from dasha.models import AntarDasha, DashaEffect
from .serializers import AntarDashaSerializer, DashaEffectSerializer
from rest_framework.pagination import PageNumberPagination

class AntarDashaListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class DashaEffectListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class AntarDashaListView(generics.ListAPIView):
    queryset = AntarDasha.objects.all().order_by('-start_date')
    serializer_class = AntarDashaSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = AntarDashaListPagination

class AntarDashaDetailView(generics.RetrieveAPIView):
    queryset = AntarDasha.objects.all()
    serializer_class = AntarDashaSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]

class DashaEffectListView(generics.ListAPIView):
    queryset = DashaEffect.objects.all().order_by('-start_date')
    serializer_class = DashaEffectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DashaEffectListPagination

class DashaEffectDetailView(generics.RetrieveAPIView):
    queryset = DashaEffect.objects.all()
    serializer_class = DashaEffectSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny] 