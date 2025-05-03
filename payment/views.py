import os
import logging
import razorpay
from media.countries import country
from media.states import states_lookup
from django.urls import reverse
from django.conf import settings
from subscription.utlity import kundli_price
from django.shortcuts import render,redirect
from django.contrib import messages
from csp.decorators import csp_update
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from subscription.forms import CheckoutForm
from csp.decorators import csp_update
from authentication.utlity import send_error_log
from django_ratelimit.decorators import ratelimit

razorpay_client = razorpay.Client(
    auth=(os.environ.get('RAZOR_KEY_ID'), os.environ.get('RAZOR_KEY_SECRET')))

payment_logger = logging.getLogger('payment')

@require_POST
@ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)
@csp_update(
    SCRIPT_SRC=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"),
    SCRIPT_SRC_ATTR=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"), 
    STYLE_SRC=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"),
    FRAME_SRC=("'self'", "https://checkout.razorpay.com", "https://api.razorpay.com", "https://lumberjack.razorpay.com"),
    CONNECT_SRC=("'self'", "https://checkout.razorpay.com", "https://api.razorpay.com", "https://lumberjack.razorpay.com"),
)
def kundli_payment_checkout(request):
    if request.method != "POST":
        messages.error(request, "Invalid request. Please use the proper flow to make the payment.")
        return redirect('kundli.premium_payment')

    form = CheckoutForm(request.POST)
    user = request.user

    if not form.is_valid() or not user.is_authenticated:
        logging.error(form.errors)
        messages.error(request, "Please enter valid details and ensure you're logged in.")
        return redirect('kundli.premium_payment')

    try:
        
        amount = int(os.environ.get('KUNDLI_PREMIMUM_PRICE', '100'))
        data = kundli_price(amount)

        # Ensure total is a valid number
        total_amount = int(float(data.get('total', amount)) * 100)  # Razorpay expects amount in paise
        billing_country = country.get(form.cleaned_data.get("country"))
        billing_state = states_lookup.get(form.cleaned_data.get("country"), {}).get(form.cleaned_data.get("state"))
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create({
            "amount": total_amount,
            "currency": "INR",
            "payment_capture": '0',
            "partial_payment": False,
            "notes": {
                "billing_email": user.email,
                "billing_name": f"{user.first_name} {user.last_name}",
                "billing_country": billing_country['name'],
                "billing_state": billing_state['name'],
                "billing_city": form.cleaned_data.get("city"),
                "billing_pincode": form.cleaned_data.get("pincode"),
            }
        })

        # Prepare Razorpay context for checkout
        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_merchant_key": settings.RAZOR_KEY_ID,
            "razorpay_amount": amount,
            "currency": "INR",
            "callback_url": reverse('kundli.payment_handle'),
        }

        return render(request, "payment/checkout.html", context)

    except Exception as e:
        logging.exception("Failed to create Razorpay order")
        send_error_log(e)
        messages.error(request, "Unable to create order at this time. Please try again later.")
        return redirect('kundli.premium_payment')

    
@csrf_exempt
@ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
def KundliPaymentHandler(request):
    payment_logger.debug("Payment handler invoked")
    payment_logger.info("POST data: %s", request.POST.dict())
    if request.method == "POST":
        try:
            payment_logger.info("Received POST request for payment handling")

            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            payment_logger.debug(f"Payment ID: {payment_id}")
            payment_logger.debug(f"Order ID: {razorpay_order_id}")
            payment_logger.debug(f"Signature: {signature}")

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            amount = int(os.environ.get('KUNDLI_PREMIMUM_PRICE', '100'))
            data = kundli_price(amount)
            total_amount = int(float(data.get('total', amount)) * 100)

            payment_logger.debug(f"Calculated Total Amount (in paise): {total_amount}")

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            payment_logger.debug(f"Signature verification result: {result}")

            if result:
                try:
                    payment_logger.info("Signature verified, attempting payment capture...")
                    razorpay_client.payment.capture(payment_id, total_amount)
                    payment_logger.info(f"Payment successfully captured.")
                    messages.success(request, "Your Payment Processed Successfully.")
                    return redirect('kundli.premium_download')
                except Exception as capture_error:
                    payment_logger.error("Payment capture failed for %s: %s", payment_id, capture_error, exc_info=True)
                    payment_logger.exception("Payment capture failed.")
                    messages.error(request, "Unable to process payment. If your balance is deducted you can write us with payment details.")
                    return redirect('kundli.premium_payment')
            else:
                payment_logger.warning("Signature verification failed.")
                messages.error(request, "Unable to process payment. If your balance is deducted you can write us.")
                return redirect('kundli.premium_payment')

        except Exception as e:
            payment_logger.exception("Exception occurred in payment handler.")
            send_error_log(e)
            messages.error(request, "Unable to process payment. If your balance is deducted you can write us with payment details.")
            return redirect('kundli.premium_payment')
    else:
        payment_logger.warning("Invalid request method for payment handler.")
        messages.error(request, "Invalid request.")
        return redirect('kundli.premium_payment')


@require_POST
@ratelimit(key='user_or_ip', rate='2/m', method='POST', block=True)
@csp_update(
    SCRIPT_SRC=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"),
    SCRIPT_SRC_ATTR=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"), 
    STYLE_SRC=("'self'", "https://checkout.razorpay.com", "https://lumberjack.razorpay.com", "'unsafe-inline'"),
    FRAME_SRC=("'self'", "https://checkout.razorpay.com", "https://api.razorpay.com", "https://lumberjack.razorpay.com"),
    CONNECT_SRC=("'self'", "https://checkout.razorpay.com", "https://api.razorpay.com", "https://lumberjack.razorpay.com"),
)
def subscription_payment_checkout(request):

    if request.method == "POST":
        form = CheckoutForm(request.POST)      
        user = request.user
        if form.is_valid() and user.is_authenticated:
            try:
                currency = 'INR'
                amount = int(os.environ.get('KUNDLI_PREMIMUM_PRICE')) * 100 
                  
                    # Create a Razorpay Order
                razorpay_order = razorpay_client.order.create(
                    dict(
                        amount=amount,
                        currency=currency,
                        payment_capture='0',
                        notes={
                        "billing_email": user.email,
                        "billing_name": f"{user.first_name} {user.last_name}",
                        "billing_country": form.cleaned_data.get("country"),
                        "billing_state": form.cleaned_data.get("state"),
                        "billing_city": form.cleaned_data.get("city"),
                        "billing_pincode": form.cleaned_data.get("pincode"),
                        }
                    ))
                
                context = {}
                
                razorpay_order_id = razorpay_order['id']
                callback_url = reverse('kundli.payment_handle')   
                context['razorpay_order_id'] = razorpay_order_id
                context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
                context['razorpay_amount'] = amount
                context['currency'] = currency
                context['callback_url'] = callback_url

                return render(request, "payment/checkout.html", context)
            except Exception as e:
                messages.error(request,"Unable to create order this time, Please try again!")
                send_error_log(e)
        else:
            messages.error(request,"Please enter a valid details!")
    else:
        messages.error(request,"Invalid request Please follow valid way to download report, Please try again!")
    
    return redirect('kundli.premium_payment')            



   
@csrf_exempt
@ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
def SubscriptionPaymentHandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
         
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = int(os.environ.get('KUNDLI_PREMIMUM_PRICE'))*100
                try:  
                    razorpay_client.payment.capture(payment_id, amount)
                    messages.success(request, "Your Payment Processed Successfully.")
                    return redirect('kundli.premium_download')
                except:
                   messages.error(request, "Unable to process payment signature failed. If your balance is deducted you can write us with payment details.")
                   return redirect('kundli.premium_payment')
            else:
                messages.error(request, "Unable to process payment.If your balance is deducted you can write us.")
                return redirect('kundli.premium_payment')
            
        except Exception as e:
            send_error_log(e)
            messages.error(request, "Unable to process payment.If your balance is deducted you can write us with payment details.")
            return redirect('kundli.premium_payment')
        

    