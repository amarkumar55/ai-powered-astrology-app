import datetime
from .models import Panchang
from django.views import View
from .forms import PanchangForm
from django.contrib import messages
from django.utils.timezone import now
from utlity.helper import store_activity
from django.shortcuts import render,redirect
from utlity.panchag import calculate_panchang
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic

# Create your views here.

@method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True), name='dispatch')
class PanchangListView(View):
    template_name = "numberlogy/driver_condutor/index.html"

    def get(self, request): 
        try:
           panchang = Panchang.objects.get(date=now().date())
           return render(request, self.template_name, {"panchang":panchang})
        except Panchang.DoesNotExist:
           messages.error(request, "Panchang for today is not generated!")
           return redirect('home.index')
        
        

@method_decorator([login_required, ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True)], name='dispatch')
class UserPersonalizedPanchang(View):
   
    template_name = "panchang/user_personalized.html"

    def get(self, request): 
        show_captcha, context = handle_captcha_logic(request, {})
        form = PanchangForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)

    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = PanchangForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
             
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                days = form.cleaned_data.get("days")
                months = form.cleaned_data.get("months")
                years = form.cleaned_data.get("years")
                hours = form.cleaned_data.get("hours")
                minutes = form.cleaned_data.get("minutes")  # Fixed field reference
                seconds = form.cleaned_data.get("seconds")  # Fixed field reference
                time_type = form.cleaned_data.get("period")
                birth_date = datetime.date(years, months, days)
                place = form.cleaned_data.get("place_of_birth")
                latitude = form.cleaned_data.get("latitude")
                longitude = form.cleaned_data.get("longitude")

        
                if time_type.lower() == "pm" and hours != 12:
                    hours += 12
                elif time_type.lower() == "am" and hours == 12:
                    hours = 0
        
                panchag_data = calculate_panchang(latitude, longitude, years,months, days, hours, minutes, seconds)
            
                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "panchang": panchag_data,
                    "birth_date": birth_date,
                    "birth_place":place,
                }
        
             
                reset_failed_attempts(request)
                store_activity(request, form.cleaned_data.copy(), "panchang_predition_generate", request.user)
                messages.success(request, "Your Personalized Panchag prediction is generated.")

                return render(request, self.template_name, {
                        "form": form,
                        "is_report_generate": True,
                        "data": data
                    }   
                )

            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha
        })

        return render(request, self.template_name, context)


