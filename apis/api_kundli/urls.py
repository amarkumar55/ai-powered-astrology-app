from django.urls import path
from .views import KundliReportListView, KundliReportDetailView

urlpatterns = [
    path('', KundliReportListView.as_view(), name='api_kundli_report_list'),
    path('<int:id>/', KundliReportDetailView.as_view(), name='api_kundli_report_detail'),
] 