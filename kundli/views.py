import os
import json
import pdfkit
import requests
import logging
from .models import Location
from .forms import KundliForm
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from utlity.helper import store_activity
from subscription.forms import CheckoutForm
from subscription.utlity import kundli_price
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .utlity import generate_kundli_details, clean_chart_data, get_valid_context_or_redirect
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic


@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), name='dispatch')
class KundliPreditionView(View):
    template_name = "kundli/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
                
                kundli = generate_kundli_details(request, form.cleaned_data.copy())

                if kundli is None:
                    increment_failed_attempts(request)
                    messages.error(request, "Something went wrong while processing your request.")
                
                else: 
                    reset_failed_attempts(request)
                   
                    if request.user.is_authenticated:
                       store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", request.user)
                    else:
                        store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", None)
                                        
                    messages.success(request, "Your Personalized Kundli prediction is generated.")
                    
                    return render(request, self.template_name, {
                        "form": form,
                        "is_report_generate": True,
                        "kundli": kundli,
                        "sade_sati_result": json.loads(kundli.sade_sati_result),
                        "sade_sati_phases": json.loads(kundli.sade_sati_phases),
                        "manglik_dosha": kundli.manglik_dosha,
                        "kaal_sarp_dosha":kundli.kaal_sarp_dosha,
                        "mahapurush_yogas":json.loads(kundli.mahapurush_yogas),
                        "gaja_kesari_yoga":kundli.gaja_kesari_yoga,
                        "budha_aditya_yoga":kundli.budha_aditya_yoga,
                        "pitra_dosha":kundli.pitra_dosha,
                        "kundli_data":clean_chart_data(kundli.kundli_data) 
                    })

            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            for field, errors in form.errors.items():
                for error in errors:
                    logging.error(f"{field}: {error}")
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha
        })

        return render(request, self.template_name, context)



@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='30/m', method='POST', block=True), name='dispatch')
class KundliPremiumView(View):
    template_name = "kundli/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "show_captcha": show_captcha,
            "is_premium" : True
        })
        return render(request, self.template_name, context)
    

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
                kundli = generate_kundli_details(request, form.cleaned_data.copy())

                if kundli is None:
                    increment_failed_attempts(request)
                    messages.error(request, "Something went wrong while processing your request.")
                else:
                    self.request.session['kundli_id'] = kundli.id
                    reset_failed_attempts(request)
                    messages.success(request, "Your Personalized Kundli prediction is generated. Please complete payment to download")
                    return redirect('kundli.premium_payment')
            
            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)



@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), name='dispatch')
class KundliPaymentProcessView(View):
    template_name = "kundli/checkout.html"
   
    def get(self, request):
        if not self.request.session.get('kundli_id'):
           messages.error(request,"Invalid request, Please contact us")
           return redirect('kundli.premium_anaysis')

        show_captcha, context = handle_captcha_logic(request, {})
        form = CheckoutForm(show_captcha=show_captcha)
        price = os.environ.get('KUNDLI_PREMIMUM_PRICE')
        data = kundli_price(price)

        context.update({
            "form": form,
            "show_captcha": show_captcha,
            "price":price,
            "gst":data['gst'],
            "total":data['total'],
            "countries":data['countries'],
        })

        return render(request, self.template_name, context)  
    
@method_decorator(login_required, name='dispatch')    
@method_decorator(
    ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), 
    name='dispatch'
)
class KundliPremiumDownloadView(View):
    template_name = "kundli/premium.html"

    def get(self, request):
        kundli_id = self.request.session.get('kundli_id')
        result = get_valid_context_or_redirect(request, kundli_id)
       
        if isinstance(result, HttpResponse):  # Redirect case
            return result
        return render(request, self.template_name, result)

    def post(self, request):
        kundli_id = self.request.session.get('kundli_id')
        result = get_valid_context_or_redirect(request,kundli_id)
        if isinstance(result, HttpResponse):  # Redirect case
            return result
        html = render_to_string("kundli/kundli_pdf.html", result) 
        pdf = pdfkit.from_string(html, False, configuration=settings.PDFKIT_CONFIG,options={"enable-local-file-access": ""})
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="kundli_report.pdf"'
        return response
    

@method_decorator(login_required, name='dispatch')    
@method_decorator(
    ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), 
    name='dispatch'
)
class KundliDownloadView(View):
    template_name = "kundli/premium.html"

    def get(self, request, kundli_id):
        result = get_valid_context_or_redirect(request,kundli_id)
        if isinstance(result, HttpResponse):  # Redirect case
            return result
        
        result['kundli_id'] = kundli_id
        return render(request, self.template_name, result)

    def post(self, request, kundli_id):
        
        result = get_valid_context_or_redirect(request, kundli_id)
       
        if isinstance(result, HttpResponse): 
            return result

        html = render_to_string("kundli/kundli_pdf.html", result) 
        pdf = pdfkit.from_string(html, False, configuration=settings.PDFKIT_CONFIG,options={"enable-local-file-access": ""})
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="kundli_report.pdf"'
        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True), name='dispatch')
class SearchLocationView(View):

    def get(self, request):
        query = request.GET.get("place", "").strip()
        location_api_key = os.environ.get('LOCATIONIQ_API_KEY')

        if not query or not location_api_key:
            return JsonResponse({"error": "No place provided"}, status=400)

        # Check local DB/cache
        exist_in_cache = Location.objects.filter(place__icontains=query).values("place", "latitude", "longitude")

        if exist_in_cache.exists():
            return JsonResponse(list(exist_in_cache), safe=False)

        # External API call
        api_url = f"https://us1.locationiq.com/v1/search.php?key={location_api_key}&q={query}&format=json"

        try:
            response = requests.get(api_url)
            data = response.json()

            if not data:
                return JsonResponse({"error": "Location not found"}, status=404)

            locations = []
            for item in data:
                # Avoid duplicates (adjusted logic)
                Location.objects.get_or_create(
                    place=item.get("display_name"),
                    defaults={
                        "latitude": round(float(item.get("lat")), 6),
                        "longitude": round(float(item.get("lon")), 6),
                    }
                )
                locations.append({
                    "place": item.get("display_name"),
                    "latitude": item.get("lat"),
                    "longitude": item.get("lon"),
                })

            return JsonResponse(locations, safe=False)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)





