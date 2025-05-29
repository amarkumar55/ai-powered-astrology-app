from . import views
from django.urls import path

urlpatterns = [
   path("", views.index, name="home.index"),
   path("about-us", views.about, name="home.about"),
   path("latest-blogs", views.blog, name="home.blog"),
   path("career", views.jobs, name="home.jobs"),
   path("our-services", views.services, name="home.services"),
   path("contact-us", views.ContactUsView.as_view(), name="home.contactus"),
   path("frequency-asked-questions", views.faqs, name="home.faqs"),
   path("terms-and-conditions", views.term_condition, name="terms_and_conditions"),
   path("privacy-policy", views.policy, name="privacy_policy"),
   path("our-pricing", views.our_plans, name="home.our_plans"),
]
