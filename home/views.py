from django.views import View
from .forms import ContactForm
from django.contrib import messages
from subscription.models import Plan
from captcha.models import CaptchaStore
from utlity.helper import store_activity
from django.shortcuts import render, redirect
from captcha.helpers import captcha_image_url
from django.contrib.auth import get_user_model
from authentication.utlity import send_error_log
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

User = get_user_model() 


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def index(request):
    return render(request, "home/index.html",{})

@ratelimit(key='user_or_ip', rate='2/m', block=True)
def about(request):
    return render(request, "home/about.html",{})


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def blog(request):
    return render(request, "home/blog.html",{})


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def jobs(request):
    return render(request, "home/career.html",{})

@ratelimit(key='user_or_ip', rate='5/m', block=True)
def services(request):
    return render(request, "home/service.html",{})


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class ContactUsView(View):
    template_name = "home/contact.html"

    def get(self, request):
        new_captcha = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_captcha)
        context = {
            'form': ContactForm(),
            'captcha_key': new_captcha,
            'captcha_image_url': image_url,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = ContactForm(request.POST)
        new_captcha = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_captcha)
        context = {
            'form': form,
            'captcha_key': new_captcha,
            'captcha_image_url': image_url,
        }

        try:
            if form.is_valid():
                contactus = form.save(commit=False)
                contactus.save()
                store_activity(request, {}, "contact_query", request.user)
                messages.success(request, "Your request has been submitted successfully. We will contact you shortly. Thank you!")
                return redirect('home.index')
            else:
                messages.error(request, "Unable to process your request currently. Please check your details.")
        except Exception as e:
            send_error_log(e)
            messages.error(request, f"Error: {e}")

        return render(request, self.template_name, context)


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def policy(request):
    return render(request, "home/policy.html",{})

@ratelimit(key='user_or_ip', rate='5/m', block=True)
def our_plans(reqest):
    plans = Plan.objects.prefetch_related('features')
    return render(reqest, "subscriptions/index.html",{"plans":plans})

@ratelimit(key='user_or_ip', rate='5/m', block=True)
def custom_404(request):
    return render(request, "includes/404.html",{})


