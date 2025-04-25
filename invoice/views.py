import pdfkit
from .models import Invoice
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

# Create your views here.


def invoice_download(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    # 2. Render the invoice into HTML
    html = render_to_string('dashboard/invoices/invoice_pdf.html', {'invoice': invoice})

    # 3. Generate PDF from HTML
    pdf = pdfkit.from_string(html, False, configuration=settings.PDFKIT_CONFIG)

    # 4. Return as downloadable file
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
    return response