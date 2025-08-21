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

from django.urls import path, include, re_path
from home import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from django.shortcuts import render
from utlity.views import DeviceDetectionDebugView


urlpatterns = [   
    path('', include('home.urls')),
    path('manage-app/admin/', include('admin_panel.urls')),
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
    path('payment/', include('payment.urls')),   
    path('api/1.0/auth/', include('apis.api_auth.urls')), 
    path('api/1.0/notes/', include('apis.api_notes.urls')),   
    path('api/1.0/invoices/', include('apis.api_invoice.urls')),  
    path('api/1.0/subscription/', include('apis.api_subscription.urls')),  
    path('api/1.0/home/', include('apis.api_home.urls')),
    path('api/1.0/payments/', include('apis.api_payment.urls')),
    path('api/1.0/panchang/', include('apis.api_panchang.urls')),
    path('api/1.0/numberlogy/', include('apis.api_numberlogy.urls')),
    path('api/1.0/loshugrid/', include('apis.api_loshugrid.urls')),
    path('api/1.0/kundli/', include('apis.api_kundli.urls')),
    path('api/1.0/horoscope/', include('apis.api_horoscope.urls')),
    path('api/1.0/dashboard/', include('apis.api_dashboard.urls')),
    path('api/1.0/dasha/', include('apis.api_dasha.urls')),
    path('api/1.0/compatibility/', include('apis.api_compatibility.urls')),
    path('api/1.0/blogs/', include('apis.api_blogs.urls')),
    path('api/1.0/notifications/', include('apis.api_notifiaction.urls')),

    path('chat/', include('chat.urls')),
    path('debug/device-detection/', DeviceDetectionDebugView.as_view(), name='debug_device_detection'),
    
    re_path(r"^.*$", views.custom_404),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def custom_permission_denied_view(request, exception):
    return render(request, "403.html", status=403)

handler403 = custom_permission_denied_view