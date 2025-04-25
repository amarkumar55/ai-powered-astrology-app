import re
from django.views import View
from .forms import LoShuGridForm
from django.shortcuts import render
from django.contrib import messages
from utlity.helper import store_activity
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from utlity.lo_shu_grid import get_number_detail, get_combination_available
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class LoShuGridView(View):
    template_name = "loshugrid/index.html"

    def get(self, request):
        
        show_captcha, context = handle_captcha_logic(request, {})
        form = LoShuGridForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)

    def post(self, request):
 
        show_captcha, context = handle_captcha_logic(request, {})
        form = LoShuGridForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
                 # Extract cleaned data from the form
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                birth_date = form.cleaned_data.get('birth_date', '')

                # Initialize a dictionary for digits 1 to 9
                numbers = {i: {"count": 0, "detail": {}} for i in range(1, 10)}

                # Extract digits from the birth_date string
                digits = [int(d) for d in re.findall(r'\d', str(birth_date)) if d != '0']
                    
                data = {
                    "name": f"{first_name} {last_name}".strip(),
                    "date_of_birth": birth_date,
                    "arrows_of_strength": [],
                    "numbers": numbers,
                    "digits": digits,
                }

                # Check for arrow combinations and add descriptions
                if 1 in digits and 5 in digits and 9 in digits:
                    data['arrows_of_strength'].append(get_combination_available('1_5_9'))
                if 4 in digits and 5 in digits and 9 in digits:
                    data['arrows_of_strength'].append(get_combination_available('4_5_9'))
                if 7 in digits and 5 in digits and 3 in digits:
                    data['arrows_of_strength'].append(get_combination_available('7_5_3'))
                if 2 in digits and 5 in digits and 8 in digits:
                    data['arrows_of_strength'].append(get_combination_available('2_5_8'))
                if 1 in digits and 4 in digits and 7 in digits:
                    data['arrows_of_strength'].append(get_combination_available('1_4_7'))
                if 3 in digits and 5 in digits and 7 in digits:
                    data['arrows_of_strength'].append(get_combination_available('3_5_7'))
                if 3 in digits and 6 in digits and 9 in digits:
                    data['arrows_of_strength'].append(get_combination_available('3_6_9'))

                # Count the occurrences of each digit
                for digit in digits:
                    numbers[digit]["count"] += 1

                # Prepare detail for each number present using the utility function
                for digit in range(1, 10):
                    if digit in digits:
                        numbers[digit]["detail"] = get_number_detail(str(digit))

                data['numbers'] = numbers
             
                reset_failed_attempts(request)
                store_activity(request, form.cleaned_data.copy(), "loshugrid_predition_generate", request.user)
                messages.success(request, "Your Lo Shu Grid prediction is generated.")

                return render(request, self.template_name, {
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


