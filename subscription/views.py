from .models import Plan
from django.views import View
from .forms import CheckoutForm
from django.db import transaction
from django.contrib import messages
from utlity.helper import store_activity
from invoice.utlity import create_invoice
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect,get_object_or_404
from subscription.utlity import create_subscription, create_data
from utlity.location_loader import get_states_by_country, get_cities_by_state
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def states_view(request, country_id):
    data = get_states_by_country(country_id)
    if not data:
        return HttpResponseNotFound("Country code not found.")
    return JsonResponse(data, safe=False)

@ratelimit(key='user_or_ip', rate='5/m', block=True)
def cities_view(request, state_id):
    data = get_cities_by_state(state_id)
    if not data:
        return HttpResponseNotFound("State code not found.")
    return JsonResponse(data, safe=False)


    
@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class CheckoutView(View):
    template_name = "subscriptions/checkout.html"
    form_class = CheckoutForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, plan_slug):
        show_captcha, context = handle_captcha_logic(request, {})
        plan, countries = create_data(plan_slug)
        context.update({
            "form": self.form_class(),
            "show_captcha": show_captcha,
            "plan":plan,
            "countries":countries,
        })

        return render(request, self.template_name, context)

    def post(self, request, plan_slug):
        show_captcha, context = handle_captcha_logic(request, {})
        form = self.form_class(request.POST,show_captcha=show_captcha)
        user = request.user

        if form.is_valid() and user.is_authenticated:
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            country = form.cleaned_data.get("country")
            state = form.cleaned_data.get("state")
            city = form.cleaned_data.get("city")
            phone_code = form.cleaned_data.get("phone_code")
            phone_number = form.cleaned_data.get("phone_number")
            billing_address = f"contact no. {phone_code} {phone_number}, {city}, {state}, {country}"

            plan = get_object_or_404(Plan.objects.prefetch_related('features'), slug=plan_slug)

            try:
                with transaction.atomic():
                    invoice = create_invoice(plan, user, name, email, billing_address)
                    subscription = create_subscription(plan, user, invoice)

                    invoice.subscription = subscription
                    invoice.save()
                reset_failed_attempts
                store_activity(request, form.cleaned_data.copy(), "subscribed to plan", request.user)
                messages.success(request, "You have successfully subscribed. Enjoy!")
                return redirect("home.index")

            except Exception as e:
                send_error_log(e)
                increment_failed_attempts(request)
                messages.error(request, "Unable to process your request currently. Please check your details.")
            
        else:
            increment_failed_attempts(request)
            messages.error(request, "Unable to process your request currently. Please check your details.")
      
        plan, countries = create_data(plan_slug)
      
        context.update({
            "form": form,
            "plan": plan,
            "countries":countries,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)