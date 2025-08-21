from .models import EmailOTP
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse_lazy
from django.contrib.auth import login
from utlity.helper import store_activity
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django_ratelimit.decorators import ratelimit
from django.utils.http import urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView, LogoutView
from .utlity import send_otp_message,send_verification_email, generate_username, handle_captcha_logic
from .utlity import send_error_log,send_password_change_email, reset_failed_attempts, increment_failed_attempts
from .forms import CustomSetPasswordForm, RegisterForm, VerifyLoginOtp, CustomLoginForm, ResendVerificationForm

User = get_user_model()

COOLDOWN_SECONDS = 60  


@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('auth.login')
    form_class = CustomSetPasswordForm  # ✅ use custom form

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        show_captcha, _ = handle_captcha_logic(self.request, {})
        kwargs['show_captcha'] = show_captcha  # ✅ custom kwarg
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, context = handle_captcha_logic(self.request, context)
        return context

    def form_valid(self, form):
        user = form.user
        send_password_change_email(user)
        store_activity(self.request, {}, "password_reset", user)
        messages.success(self.request, "Your password has been reset successfully. You can now log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        _, context = handle_captcha_logic(self.request, self.get_context_data(form=form))
        return self.render_to_response(context)
    
    
# REGISTER NEW USER INTO SYSTEM
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class RegisterView(FormView):
    template_name = 'authentication/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('auth.login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard.index')  
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, context = handle_captcha_logic(self.request, context)
        return context

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.username = generate_username(user.first_name)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            current_date = timezone.now()
            user.date_joined = current_date
            user.last_login = current_date
            user.is_active = True
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            
            if user.id:
                store_activity(self.request, form.cleaned_data.copy(), "account_created", user)
            send_verification_email(self.request, user)

            messages.success(self.request, "Your account was created successfully. Please log in.")
            return super().form_valid(form)

        except Exception as e:
            send_error_log(e)
            messages.error(self.request, "Error during registration. Please try again.")
            return self.form_invalid(form)  # fall back to the form with errors

    def form_invalid(self, form):
        
        messages.error(self.request, "There was an error with your registration.")
        return super().form_invalid(form)



@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('dashboard.index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, context = handle_captcha_logic(self.request, context)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard.index')  
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        show_captcha, _ = handle_captcha_logic(self.request, {})
        kwargs['show_captcha'] = show_captcha
        return kwargs

    def form_valid(self, form):
        # Logic for when the form is valid
        user = form.get_user()

        if  user.is_temporarily_disabled:
            self.request.session['temporarily_user_email'] = self.request.POST.get('username')
            return render(self.request, "dashboard/account/profile_disable.html", {"deletion_type": "temporarily"})
         
        if user.is_permanent_disabled:
            
            return render(self.request, "dashboard/account/profile_disable.html", {"deletion_type": "permanent"})

        # Handle 2FA
        if user.two_factor_enabled:
            self.request.session['remember_me'] = self.request.POST.get('remember')
            self.request.session['pre_2fa_user_id'] = user.pk
            send_otp_message(user.email, "LOGIN OTP")
            return redirect('verify_login_otp')
        else:
            remember_me = self.request.POST.get('remember')
            login(self.request, user)
          
            if user.is_authenticated and not user.is_email_verified:
                self.request.session['unverified_email'] = user.email
            else:
                self.request.session.pop('unverified_email', None)
        
            reset_failed_attempts(self.request)
            if remember_me:
                self.request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                self.request.session.set_expiry(0)
            store_activity(self.request, {}, "account_login", user)
            messages.success(self.request, "Login successful!")
            return redirect(self.success_url)

    def form_invalid(self, form):
        # Logic for when the form is invalid
        increment_failed_attempts(self.request)
        messages.error(self.request, "Invalid credentials. Please try again.")
        return super().form_invalid(form)



@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class VerifyLoginOTPView(FormView):
    template_name = 'authentication/verify_login_otp.html'
    form_class = VerifyLoginOtp
    success_url = reverse_lazy('dashboard.index')  # Redirect after successful login

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_id = self.request.session.get('pre_2fa_user_id')
        if not user_id:
            return redirect('auth.login')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(self.request, "User not found. Please try again.")
            return redirect('auth.login')

        context['email'] = user.email

        _, context = handle_captcha_logic(self.request, context)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        show_captcha, _ = handle_captcha_logic(self.request, {})
        kwargs['show_captcha'] = show_captcha
        return kwargs

    def form_valid(self, form):
        user_id = self.request.session.get('pre_2fa_user_id')
        remember_me = self.request.session.get('remember_me')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(self.request, "User not found. Please try again.")
            return redirect('auth.login')

        entered_otp = form.cleaned_data.get('otp')

        try:
            otp_obj = EmailOTP.objects.filter(email=user.email).first()

            if otp_obj and otp_obj.verify_otp(entered_otp) and not otp_obj.is_expired():
                otp_obj.delete()  # OTP used
                store_activity(self.request, {}, "account_login", user)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(self.request, user)
                reset_failed_attempts(self.request)

                if remember_me:
                    self.request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    self.request.session.set_expiry(0)

                del self.request.session['pre_2fa_user_id']
                del self.request.session['remember_me']

                messages.success(self.request, 'Login successful.')
                return redirect(self.success_url)
            else:
                increment_failed_attempts(self.request)
                messages.error(self.request, 'Invalid or expired OTP.')

        except Exception as e:
            increment_failed_attempts(self.request)
            send_error_log(e)
            messages.error(self.request, 'Unable to verify OTP. Please try again later.')

        return self.form_invalid(form)

    def form_invalid(self, form):
        increment_failed_attempts(self.request)
        messages.error(self.request, 'Invalid OTP format.')
        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard.index')
        return super().dispatch(request, *args, **kwargs)




@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='20/m', method='GET', block=True), name='dispatch')
class CustomLogoutView(LogoutView):
    next_page = 'auth.login'  # Redirect after logout

    def dispatch(self, request, *args, **kwargs):
        # Custom logout logic
        store_activity(request, {}, "account_logout", request.user)
        messages.success(request, "Logged out successfully.")
        return super().dispatch(request, *args, **kwargs)



@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class ProcessAccountVerificationView(View):
    
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            messages.success(request, "Email verified successfully.")
            return redirect('auth.login')
        else:
            messages.error(request, "Invalid or expired link. Please try resending the verification email.")
            return redirect('resend_verification')
        
    

@method_decorator(ratelimit(key='user_or_ip', rate='20/m', block=True), name='dispatch')
class ResendVerificationView(View):
    template_name = 'authentication/verify_notice.html'

    def get_user(self, request):
        email = request.session.get('unverified_email')
        if not email:
            return None
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        user = self.get_user(request)
        if not user:
            return redirect('auth.login')

        if user.is_email_verified:
            return redirect('dashboard.index')

        show_captcha, context = handle_captcha_logic(request, {})
        form = ResendVerificationForm(show_captcha=show_captcha)
        context.update({'form': form, 'user': user})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = self.get_user(request)
        if not user:
            return redirect('auth.login')

        if user.is_email_verified:
            return redirect('dashboard.index')

        show_captcha, context = handle_captcha_logic(request, {})
        form = ResendVerificationForm(request, data=request.POST, show_captcha=show_captcha)

        if form.is_valid():
            cooldown_key = f"email_verification_cooldown_{user.pk}"
            if cache.get(cooldown_key):
                messages.error(request, "Please wait before requesting again.")
            else:
                send_verification_email(request, user)
                cache.set(cooldown_key, True, timeout=COOLDOWN_SECONDS)
                reset_failed_attempts(request)
                messages.success(request, "Verification email sent.")
                return redirect('auth.login')
        else:
            increment_failed_attempts(request)
            messages.error(request, "Please correct the errors below.")
            _, context = handle_captcha_logic(request, {})

        context.update({'form': form, 'user': user})
        return render(request, self.template_name, context)



class AccountRestoreView(View):
    def get(self, request, *args, **kwargs):
        email = request.session.get('temporarily_user_email')
      
        if not email:
            return redirect('auth.login')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('auth.login')

        user.is_temporarily_disabled = False
        user.is_profile_block = False
        user.save()
        store_activity(self.request, {}, "account_login", user) 
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        request.session.pop('temporarily_user_email')
        
        login(request, user)

        return redirect('dashboard.index')
