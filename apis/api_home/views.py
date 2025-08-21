from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from home.models import ContactQuery
from .serializers import ContactQuerySerializer,WalletSerializer,UserActivitySerializer,WalletTransactionSerializer
from authentication.models import Wallet,WalletTransaction
from rest_framework.pagination import PageNumberPagination
from authentication.models import UserActivity

class ContactQueryListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class WalletBalancePagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class WalletTransactionsPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100


class ActivityPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20

class ContactQueryListView(generics.ListAPIView):
    serializer_class = ContactQuerySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ContactQueryListPagination
    
    def get_queryset(self):
        return ContactQuery.objects.using(self.request.db).all().order_by('-created_at')

class ContactQueryDetailView(generics.RetrieveAPIView):
    serializer_class = ContactQuerySerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return ContactQuery.objects.using(self.request.db).all()


class ContactQueryCreateView(generics.CreateAPIView):
    serializer_class = ContactQuerySerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [TokenAuthentication]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['using'] = self.request.db
        return context
    

class WalletBalanceView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Or change if needed
    serializer_class = WalletSerializer
  
    def get_object(self):
        return Wallet.objects.get(user=self.request.user)
    
class WalletTransactionsView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = WalletTransactionsPagination
    serializer_class = WalletTransactionSerializer  # add this if you haven't

    def get_queryset(self):
        wallet_id = self.kwargs['wallet_id']
        return WalletTransaction.objects.using(self.request.db).filter(wallet_id=wallet_id).order_by('-created_at')
class UserActivitiyView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = ActivityPagination
    serializer_class = UserActivitySerializer
    
    def get_queryset(self):
        return UserActivity.objects.using(self.request.db).filter(user=self.request.user).all().order_by('-created_at')
    
