from django.urls import path
from .views import ContactQueryListView, ContactQueryDetailView, ContactQueryCreateView,WalletBalanceView,WalletTransactionsView,UserActivitiyView

urlpatterns = [
    path('', ContactQueryListView.as_view(), name='api_home_contact_list'),
    path('contact/create/', ContactQueryCreateView.as_view(), name='api_home_contact_create'),
    path('<int:id>/', ContactQueryDetailView.as_view(), name='api_home_contact_detail'),
    path('wallet/balance/', WalletBalanceView.as_view(), name='api_home_wallet_balance'),
    path('wallet/<int:wallet_id>/transactions/', WalletTransactionsView.as_view(), name='api_home_wallet_transaction'),
    path('activity/', UserActivitiyView.as_view(), name='api_user_activity'),
] 