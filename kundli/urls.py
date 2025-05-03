from . import views
from django.urls import path

urlpatterns = [
   path("index", views.KundliPreditionView.as_view(), name="kundli.index"),
   path("premium/anaysis", views.KundliPremiumView.as_view(), name="kundli.premium_anaysis"),
   path("premium/payment-process", views.KundliPaymentProcessView.as_view(), name="kundli.premium_payment"),
   path("premium/download", views.KundliPremiumDownloadView.as_view(), name="kundli.premium_download"),
   path("download/<int:kundli_id>", views.KundliDownloadView.as_view(), name="dashboard.kundli_view"),
   path("search-location", views.SearchLocationView.as_view(), name="search_location"),
]
