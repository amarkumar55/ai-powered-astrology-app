from django.urls import path
from .views import UserInvoiceListView, InvoiceDetailView, InvoiceDownloadView

urlpatterns = [
    path('list/', UserInvoiceListView.as_view(), name='api_invoices'),
    path('<str:invoice_number>/', InvoiceDetailView.as_view(), name='api_invoice_detail'),
    path('<str:invoice_number>/download/', InvoiceDownloadView.as_view(), name='api_invoice_download'),
] 