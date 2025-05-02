from . import views
from django.urls import path

urlpatterns = [
    path("download/<str:invoice_number>", views.invoice_download, name="invoice.download"),
]