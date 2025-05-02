from . import views
from django.urls import path

urlpatterns = [
    path("index", views.LoShuGridView.as_view(), name="loshugrid.index")
]