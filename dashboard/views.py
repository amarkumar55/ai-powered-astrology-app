from django.views import View
from datetime import date, time
from invoice.models import Invoice
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from utlity.helper import store_activity
from authentication.models import EmailOTP
from django.core.paginator import Paginator
from django.shortcuts import render,redirect
from authentication.models import UserActivity
from subscription.models import UserTransaction
from subscription.models import UserSubscription
from django_ratelimit.decorators import ratelimit
from utlity.location_loader import get_all_timezone
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model,logout
from django.contrib.auth.decorators import login_required
from authentication.utlity import send_otp_message, send_error_log
from .utlity import handle_profile_upload, get_cache_key, get_attempt_key
from .forms import ProfileForm, AccountDeleteForm, DisableTwoFactorForm,Enable2FAForm,VerifyOTPForm, VerifyEmailChangeForm, VerifyEmailChangeOTP

# Create your views here.
User = get_user_model()

OTP_EXPIRY_MINUTES = 5
OTP_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required
def index(request):
    subscription = UserSubscription.objects.filter(user=request.user).select_related('plan').prefetch_related('plan__features').first()  
    return render(request, "dashboard/index.html", {"subscription": subscription})

@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required()
def invoices(request):
    invoices = Invoice.objects.filter(user=request.user)
    paginator = Paginator(invoices, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "dashboard/invoices/index.html", {"page_obj": page_obj})


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required()
def get_payment_history(request):

    transactions = UserTransaction.objects.filter(
        user=request.user,
        refund_id__isnull=True
    ).select_related('invoice')

    paginator = Paginator(transactions, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/payment/index.html", {"page_obj": page_obj})


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required()
def get_refund_history(request):
    transactions = UserTransaction.objects.filter(
        user=request.user,
        refund_id__isnull=False
    ).select_related('invoice')

    paginator = Paginator(transactions, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/payment/refund.html", {"page_obj": page_obj})


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required()
def get_your_activity(request):
    activities = UserActivity.objects.filter(user=request.user).order_by('-action_date_time')[:10]
    return render(request, "dashboard/activity/index.html", {"activities":activities})


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required()
def get_setting(request):
    setting = request.user
    return render(request, "dashboard/setting/index.html", {"setting":setting})


@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class ProfileUpdateView(View):
    template_name = "dashboard/profile/index.html"
    form_class = ProfileForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        timezones = get_all_timezone()
        return render(request, self.template_name, {"form": form, "profile": request.user, "timezones": timezones})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        timezones = get_all_timezone()

        if form.is_valid():
            try:
                user = request.user
              
                cd = form.cleaned_data

                # Password check
                if not user.check_password(cd["password"]):
                    messages.error(request, "Invalid current password!")
                    return render(request, self.template_name, {"form": form, "profile": user, "timezones": timezones})

                # Username uniqueness
                if user.username != cd["username"] and User.objects.filter(username=cd["username"]).exclude(id=user.id).exists():
                    messages.error(request, "Username is already taken.")
                    return render(request, self.template_name, {"form": form, "profile": user, "timezones": timezones})

                # Convert time to 24-hour format
                hours = cd["hours"]
                if cd["time_format"] == 'PM' and hours != 12:
                    hours += 12
                elif cd["time_format"] == 'AM' and hours == 12:
                    hours = 0
   
                # Update fields
                user.first_name = cd["first_name"]
                user.last_name = cd["last_name"]
                user.username = cd["username"]
                user.gender = cd["gender"]
                user.birth_date = date(cd["year"], cd["month"], cd["day"])
                user.birth_time = time(hours, cd["minutes"], cd["seconds"])
                user.timezone = cd["timezone"]
                user.birth_place = cd["place"]
                user.notification_preference = bool(cd["notification_preference"])
                user.time_format = cd['time_format']

                # Handle profile picture
                if cd.get("profile"):
                    user.profile_picture = handle_profile_upload(cd["profile"], cd["username"])

                user.save()
                store_activity(request, {} , "profile update", user)
                messages.success(request, "Your profile was updated successfully!")
                return redirect("dashboard.get_profile")

            except Exception as e:
                send_error_log(e)
                messages.error(request, f"Unable to update your profile: {str(e)}")
        else:
            messages.error(request, "Unable to update your profile: missing or invalid details")
        return render(request, self.template_name, {"form": form, "profile": request.user, "timezones": timezones})
    

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class AccountDeleteView(View):
    template_name = "dashboard/account/index.html"
    success_template = "dashboard/account/profile_disable.html"

    def get(self, request):
        form = AccountDeleteForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AccountDeleteForm(request.POST, request.FILES)
        user = request.user

        if form.is_valid():
            try:
                input_password = form.cleaned_data.get("password")
                delete_type = form.cleaned_data.get("delete_type")

                if not user.check_password(input_password):
                    messages.error(request, "Invalid current password!")
                    return render(request, self.template_name, {"form": form})

                if delete_type == "temp":
                    user.is_temporarily_disabled = True
                elif delete_type == "permanent":
                    user.is_parament_disabled = True

                user.is_is_profile_block = True
                user.save()
                store_activity(request, form.cleaned_data.copy(), "account delete", user)
                logout(request)
              
                messages.success(request, "Your profile has been deleted successfully!")

                return render(request, self.success_template, {
                    "deletion_type": delete_type
                })

            except Exception as e:
                send_error_log(e)
                messages.error(request, f"Unable to delete your profile: {str(e)}")
        else:
            messages.error(request, "Unable to delete your profile due to invalid form.")

        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class DisableTwoFactorView(View):
    template_name = 'dashboard/setting/enable_2fa.html'

    def get(self, request):
        form = DisableTwoFactorForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = DisableTwoFactorForm(request.POST)
        if form.is_valid():
            try:
                request.user.two_factor_enabled = False
                request.user.save()
                store_activity(request, {}, "disabled two factor auth", request.user)
                messages.success(request, 'Two factor authentication is disabled for your account.')
                return redirect('dashboard.index')
            except Exception as e:
                send_error_log(e)
                messages.error(request, "Something went wrong while disabling 2FA.")

        return render(request, self.template_name, {"form": form})
    

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='200/m', method='POST', block=True), name='dispatch')
class EnableTwoFactorView(View):
    template_name = 'dashboard/setting/enable_2fa.html'

    def get(self, request):
        form = Enable2FAForm()
        return render(request, self.template_name, {
            "form": form,
        })

    def post(self, request):

        form = Enable2FAForm(request.POST)
        
        if form.is_valid():
            try:
                # Send OTP via email
                email = request.user.email
                send_otp_message(email, "Your OTP for 2FA")
                
                # Notify user about OTP
                messages.success(request, 'OTP sent to your email. Please enter it below.')
                
                # Prepare the OTP verification form
                form = VerifyOTPForm()
                
                # Render with post-email form
                return render(request, self.template_name, {
                    'post_email_enter': True,
                    'form': form,
                })

            except Exception as e:
                # Log error and notify user
                send_error_log(e)
                messages.error(request, 'Unable to send OTP right now. Please try later.')
        
        else:
         
            messages.error(request, 'Invalid data. Please try again.')

        # In case of form errors, return the original form with errors
        return render(request, self.template_name, {"form": form})
    

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class VerifyTwoFactorOTPView(View):
 
    template_name = 'dashboard/setting/enable_2fa.html'

    def post(self, request):
        form = VerifyOTPForm(request.POST)

        if form.is_valid():
           
            otp_entered = request.POST.get('email_otp', '').strip()
        

            try:
                device = EmailOTP.objects.get(email='amar@astrolive.com')
            except EmailOTP.DoesNotExist:
                messages.error(request, 'otp not matched.')
                return render(request, self.template_name, {'post_email_enter': True})

            if request.user.two_factor_enabled:
                messages.error(request, '2FA is already enabled for your account.')
                return redirect('dashboard.index')

            if device.is_expired():
                messages.error(request, 'OTP expired. Please request a new OTP.')
            elif device.verify_otp(otp_entered):
                request.user.two_factor_enabled = True
                request.user.save()
                store_activity(request, {}, "enabled two factor auth", request.user)
                messages.success(request, 'Two-Factor Authentication enabled successfully.')
                return redirect('dashboard.index')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            print("form invalid")
            messages.error(request, 'Unable to process your request. Please try again.')

        return render(request, self.template_name, {'post_email_enter': True})


@ratelimit(key='user_or_ip', rate='20/m', block=True)
@login_required
def change_email_view(request):
    form = VerifyEmailChangeForm()
    return render(request, 'dashboard/setting/change_email.html', { 'form': form})


@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class SendOTPForEmailChangeView(View):
    def post(self, request):
        form = VerifyEmailChangeForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Invalid form inputs'}, status=400)

        try:
            old_email = request.POST.get('old_email')
            new_email = request.POST.get('new_email')

            if not old_email or not new_email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

            if not request.user.check_password(request.POST.get('password')):
                return JsonResponse({'status': 'error', 'message': 'Invalid Current Password'}, status=400)

            if User.objects.filter(email=new_email).exists():
                return JsonResponse({'status': 'error', 'message': 'Your entered new email is already in use'}, status=400)

            cooldown_key = get_cache_key(old_email)

            if cache.get(cooldown_key):
                return JsonResponse({'status': 'cooldown', 'message': 'Please wait before requesting another OTP'}, status=429)

            send_otp_message(old_email,"Your OTP for Email Verification")
            send_otp_message(new_email,"Your OTP for Email Verification")

            cache.set(cooldown_key, True, OTP_COOLDOWN_SECONDS)
        except Exception as e:
            send_error_log(e)
            return JsonResponse({'status': 'error', 'message': 'Unable to send otp.'})

        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True), name='dispatch')
class VerifyOTPForEmailChangeView(View):
    def post(self, request):
        form = VerifyEmailChangeOTP(request.POST)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Please enter valid inputs'}, status=400)

        old_email = request.POST.get('old_email')
        new_email = request.POST.get('new_email')
        old_email_otp = request.POST.get('old_email_otp')
        new_email_otp = request.POST.get('new_email_otp')

        if not old_email_otp or not new_email_otp:
            return JsonResponse({'status': 'error', 'message': 'Incorrect OTPs'}, status=400)

        try:
            old_otp = EmailOTP.objects.get(email=old_email)
            new_otp = EmailOTP.objects.get(email=new_email)
        except EmailOTP.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Incorrect OTPs'}, status=400)

        if old_otp.is_expired() or new_otp.is_expired():
            return JsonResponse({'status': 'error', 'message': 'OTP expired'}, status=410)

        attempt_key = get_attempt_key(old_email)
        attempts = cache.get(attempt_key, 0)

        if attempts >= MAX_ATTEMPTS:
            return JsonResponse({'status': 'blocked', 'message': 'Too many attempts. Please request a new OTP'}, status=429)

        if old_otp.verify_otp(old_email_otp) and new_otp.verify_otp(new_email_otp):
            cache.delete(attempt_key)
            request.user.email = new_email
            request.user.save()
            store_activity(request, {"new_old":new_email,"old_email":old_email} , "changed email for account", request.user)
            return JsonResponse({'status': 'success', 'message': 'OTP verified'})
        else:
            cache.set(attempt_key, attempts + 1, 600)  # 10-minute expiry
            return JsonResponse({'status': 'error', 'message': 'Incorrect OTP'}, status=401)