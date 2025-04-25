"""
URL configuration for astro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from home import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from django.shortcuts import render

urlpatterns = [   
    path('', include('home.urls')),
    path('manage-app/admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('lo-shu-gird-preditions/', include('loshugrid.urls')),
    path('numberlogy/', include('numberlogy.urls')),
    path('kundli-preditions/', include('kundli.urls')),
    path('compatibility-preditions/', include('compatibility.urls')),
    path('dasha-and-antardasha-preditions/', include('dasha.urls')),
    path('horoscope-preditions/', include('horoscope.urls')),
    path('panchang-preditions/', include('panchang.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('subscription/', include('subscription.urls')),
    path('invoices/',include('invoice.urls')), 
    path('captcha/', include('captcha.urls')),   
    re_path(r"^.*$", views.custom_404),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def custom_permission_denied_view(request, exception):
    return render(request, "403.html", status=403)

handler403 = custom_permission_denied_view