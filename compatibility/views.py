import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import CompatibilityForm
from utlity.helper import store_activity
from utlity.panchag import calculate_nakshatra
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from utlity.compatibility import ashtakoot_compatibility
from utlity.dasha_antradasha import calculate_moon_longitude
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic

# Create your views here.
@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class CompatibilityView(View):
    template_name = "compatibility/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = CompatibilityForm(show_captcha=show_captcha)
        tag = request.GET.get('tag', '').strip()
        session_key = f'match_result_{tag}'
        data = request.session.get(session_key)
        is_report_generate = data is not None

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "show_captcha": show_captcha,
            "compatibility_scores": data.get("compatibility_scores") if data else None,
            "total_score": data.get("total_score") if data else None,
            "boy_name": data.get("boy_name") if data else None,
            "girl_name": data.get("girl_name") if data else None,
        })

        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = CompatibilityForm(request.POST, show_captcha=show_captcha)
        if form.is_valid():
            try:
                boy_name = form.cleaned_data.get('boy_full_name', '')
                girl_name = form.cleaned_data.get('girl_full_name', '')

                # Extract birth data
                bdays = form.cleaned_data.get("boy_days")
                bmonths = form.cleaned_data.get("boy_months")
                byears = form.cleaned_data.get("boy_years")
                bhours = form.cleaned_data.get("boy_hours")
                bminutes = form.cleaned_data.get("boy_minutes")  
                bseconds = form.cleaned_data.get("boy_seconds")
                b_time_type = form.cleaned_data.get("boy_time_type")
                b_lat = form.cleaned_data.get("boy_latitude")
                b_log = form.cleaned_data.get("boy_longitude")

                gdays = form.cleaned_data.get("girl_days")
                gmonths = form.cleaned_data.get("girl_months")
                gyears = form.cleaned_data.get("girl_years")
                ghours = form.cleaned_data.get("girl_hours")
                gminutes = form.cleaned_data.get("girl_minutes")  
                gseconds = form.cleaned_data.get("girl_seconds")
                g_time_type = form.cleaned_data.get("girl_time_type")
                g_lat = form.cleaned_data.get("girl_latitude")
                g_log = form.cleaned_data.get("girl_longitude")

                # Convert 12-hour to 24-hour time
                if b_time_type.lower() == "pm" and bhours != 12:
                    bhours += 12
                elif b_time_type.lower() == "am" and bhours == 12:
                    bhours = 0

                if g_time_type.lower() == "pm" and ghours != 12:
                    ghours += 12
                elif g_time_type.lower() == "am" and ghours == 12:
                    ghours = 0

                # Get Moon and Nakshatra
                boy_moon = calculate_moon_longitude(b_lat, b_log, byears, bmonths, bdays, bhours, bminutes, bseconds)
                boy_nakshatra = calculate_nakshatra(boy_moon)

                girl_moon = calculate_moon_longitude(g_lat, g_log, gyears, gmonths, gdays, ghours, gminutes, gseconds)
                girl_nakshatra = calculate_nakshatra(girl_moon)

                match = ashtakoot_compatibility(boy_nakshatra, girl_nakshatra)
                reset_failed_attempts(request)

                match_data = [
                    {"label": "Varna", "score": match.get('varna_score', 0), "max": 1},
                    {"label": "Vashya", "score": match.get('vasha_score', 0), "max": 2},
                    {"label": "Tara", "score": match.get('tara_score', 0), "max": 3},
                    {"label": "Yoni", "score": match.get('yoni_score', 0), "max": 4},
                    {"label": "Graha Maitri", "score": match.get('graha_maitry_score', 0), "max": 5},
                    {"label": "Gana", "score": match.get('gana_score', 0), "max": 6},
                    {"label": "Bhakoot", "score": match.get('bhakoot_score', 0), "max": 7},
                    {"label": "Nadi", "score": match.get('nadi_score', 0), "max": 8}, 
                ]

     
                if request.user.is_authenticated:
                    store_activity(self.request, form.cleaned_data.copy() , "generated compatibility predition", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "generated compatibility predition", None)
                
              
                messages.success(request, "Your Compatibility prediction is generated.")

                data = {
                    "compatibility_scores": match_data,
                    "total_score": match['total_score'],
                    "boy_name": boy_name,
                    "girl_name": girl_name,
                }
                
                tag = uuid.uuid4().hex 
                request.session[f'match_result_{tag}'] = data
    
                return redirect(f"{reverse('matching.index')}?tag={tag}")   

            except Exception as e:
                increment_failed_attempts(request)
                _, context = handle_captcha_logic(request, {})
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            _, context = handle_captcha_logic(request, {})
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({'form': form, "is_report_generate": False})
        return render(request, self.template_name, context)
