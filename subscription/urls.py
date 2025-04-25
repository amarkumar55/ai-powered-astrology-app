from . import views
from django.urls import path

urlpatterns = [
    path("checkout/<slug:plan_slug>", views.CheckoutView.as_view(), name="subscription.checkout"), 
    path("states/<int:country_id>", views.states_view, name='states'),
    path("cities/<int:state_id>", views.cities_view, name='cities'),
]
 