from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from invoice.models import Invoice
from .serializers import InvoiceSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import pdfkit
from rest_framework.pagination import PageNumberPagination

class UserInvoiceListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class UserInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserInvoiceListPagination

    def get_queryset(self):
        return Invoice.objects.using(self.request.db).filter(user=self.request.user).order_by('-created_at')

class InvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'invoice_number'

    def get_queryset(self):
        return Invoice.objects.using(self.request.db).filter(user=self.request.user)

class InvoiceDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, invoice_number):
        invoice = get_object_or_404(
          Invoice.objects.using(request.db).filter(invoice_number=invoice_number, user=request.user)
        )
        html = render_to_string('dashboard/invoices/invoice_pdf.html', {'invoice': invoice})
        pdf = pdfkit.from_string(html, False, configuration=getattr(settings, 'PDFKIT_CONFIG', None))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
        return response 