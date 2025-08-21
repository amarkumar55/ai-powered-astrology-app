import uuid
from django.views import View
from .forms import NameNumberForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from utlity.helper import store_activity
from loshugrid.forms import LoShuGridForm
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from utlity.driver_condutor import get_combination_available, get_number_detail
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic
from utlity.name_number import get_name_number_digit, get_name_number_mean, get_name_number_compatibility, calculate_numbers,calculate_destiny_number, calculate_life_path_number
from utlity.name_number import  get_destiny_number_significance, calculate_personality_number, get_personality_number_significance, get_life_path_number_significance

# Get Name Number Prediction

@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class DriverConductorView(View):
    template_name = "numberlogy/driver_condutor/index.html"

    def get(self, request): 
        tag = request.GET.get('tag', '').strip()
        session_key = f'driver_and_conductor_result_{tag}'

        data = request.session.get(session_key)
        is_report_generate = data is not None
        show_captcha, context = handle_captcha_logic(request, {})
        form = LoShuGridForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "show_captcha": show_captcha,
            "data": data
        })
        return render(request, self.template_name, context)
    


    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = LoShuGridForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
             
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                birth_date = form.cleaned_data.get('birth_date', '')

                # Calculate driver and conductor numbers
                number_info = calculate_numbers(birth_date)

                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "driver": number_info.get('driver_number'),
                    "conductor": number_info.get('conductor_number'),
                    "driver_description": get_number_detail("driver", number_info.get('driver_number')),
                    "conductor_description": get_number_detail("conductor", number_info.get('conductor_number')),
                    "pair_description": get_combination_available(number_info.get('driver_number'), number_info.get('conductor_number')),
                }

        
             
                reset_failed_attempts(request)
             
                tag = uuid.uuid4().hex 
                request.session[f'driver_and_conductor_result_{tag}'] = data
              
                if request.user.is_authenticated:
                    store_activity(request, form.cleaned_data.copy(), "driver_conductor_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "name_number_predition_generate", None)
             
                messages.success(request, "Your Driver and Conductor prediction has been generated successfully.")

                return redirect(f"{reverse('numerology.driver_conductor.index')}?tag={tag}")

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


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class NameNumberView(View):
    
    template_name = "numberlogy/name_number/index.html"

    def get(self, request): 
    
        tag = request.GET.get('tag', '').strip()
        session_key = f'name_number_result_{tag}'

        data = request.session.get(session_key)
        is_report_generate = data is not None

        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "data": data,
            "show_captcha": show_captcha,
        })

        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(request.POST, show_captcha=show_captcha)
      
        if form.is_valid():
            try:
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')

                full_name = f"{first_name} {last_name}".strip()
                name_number = get_name_number_digit(full_name)

               

                data = {
                    "name": full_name,
                    "name_number": name_number,
                    "name_number_description": get_name_number_mean(name_number),
                    "name_number_compatibility": get_name_number_compatibility(name_number),
                }
              
                tag = uuid.uuid4().hex 

                request.session[f'name_number_result_{tag}'] = data

                reset_failed_attempts(request)
                if request.user.is_authenticated:
                    store_activity(request, form.cleaned_data.copy(), "name_number_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "name_number_predition_generate", None)
                
                messages.success(request, "Your Name Number prediction has been generated successfully.")

                return redirect(f"{reverse('numerology.name_number.index')}?tag={tag}")
               
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


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class LifePathView(View):
    template_name = "numberlogy/life_path_number/index.html"

    def get(self, request): 

        tag = request.GET.get('tag', '').strip()
        session_key = f'life_path_result_{tag}'

        data = request.session.get(session_key)
        is_report_generate = data is not None
    
        show_captcha, context = handle_captcha_logic(request, {})
      
        form = LoShuGridForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "show_captcha": show_captcha,
            "data": data,
        })
        return render(request, self.template_name, context)
    


    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = LoShuGridForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
             
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                birth_date = form.cleaned_data.get('birth_date', '')

                # Calculate driver and conductor numbers
                life_path_number = calculate_life_path_number(birth_date)

                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "life_path_number":life_path_number,
                    "life_path_number_description":get_life_path_number_significance(life_path_number),
                }
    
                tag = uuid.uuid4().hex 

                request.session[f'life_path_result_{tag}'] = data
              
                reset_failed_attempts(request)
              
                if request.user.is_authenticated:
                    store_activity(request, form.cleaned_data.copy(), "life_path_predition_generate", request.user)   
                else:
                    store_activity(request, form.cleaned_data.copy(), "life_path_predition_generate", None)
               
                
                messages.success(request, "Your Life Path Number prediction has been generated successfully.")

                return redirect(f"{reverse('numerology.life_path_number.index')}?tag={tag}")

            
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




@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class DestinyPathView(View):
    template_name = "numberlogy/destiny_number/index.html"

    def get(self, request): 
        tag = request.GET.get('tag', '').strip()
        session_key = f'destiny_number_result_{tag}'

        data = request.session.get(session_key)
        is_report_generate = data is not None
    
        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "data": data,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)
    


    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
             
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
         
                # Calculate driver and conductor numbers
                destiny_number = calculate_destiny_number(first_name + " "+ last_name)


                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "destiny_number": destiny_number,
                    "destiny_number_description": get_destiny_number_significance(destiny_number),
                }
    
                reset_failed_attempts(request)

                tag = uuid.uuid4().hex 

                request.session[f'destiny_number_result_{tag}'] = data

                if request.user.is_authenticated:
                    store_activity(request, form.cleaned_data.copy(), "destiny_number_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "destiny_number_predition_generate", None)
              
                messages.success(request, "Your  Number prediction has been generated successfully.")

                return redirect(f"{reverse('numerology.destiny_number.index')}?tag={tag}")

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




@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class PersonalityNumberView(View):
    template_name = "numberlogy/personality_number/index.html"

    def get(self, request): 
        tag = request.GET.get('tag', '').strip()
        session_key = f'personality_number_result_{tag}'

        data = request.session.get(session_key)
        is_report_generate = data is not None
    
        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "data": data,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)
    


    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = NameNumberForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
             
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')

                # Calculate driver and conductor numbers
                personality_number = calculate_personality_number(first_name + " "+last_name)

                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "personality_number": personality_number,
                    "personality_number_description": get_personality_number_significance(personality_number),
                }
    
                tag = uuid.uuid4().hex 

                request.session[f'personality_number_result_{tag}'] = data
    
                reset_failed_attempts(request)
                if request.user.is_authenticated:
                    store_activity(request, form.cleaned_data.copy(), "personality_number_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "personality_number_predition_generate", None)
              
                messages.success(request, "Your personality number prediction has been generated successfully.")

                return redirect(f"{reverse('numerology.personality_number.index')}?tag={tag}")
            

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
    


@method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True), name='dispatch')
class AngelNumberView(View):
    template_name = "numberlogy/angel_number/index.html"

    def get(self, request): 
        return render(request, self.template_name, {})

