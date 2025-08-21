import json
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from .models import ChatRoom, Payment, VideoCall
from .forms import PaymentForm
from utlity.helper import store_activity

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required
def initiate_payment(request, chat_id):
    """Initiate payment for a chat session"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            amount = chat_room.total_cost
            
            # Create payment record
            payment = Payment.objects.create(
                chat_room=chat_room,
                user=request.user,
                vendor=chat_room.vendor,
                amount=amount,
                payment_method=payment_method,
                description=f"Payment for chat session with {chat_room.vendor.full_name}"
            )
            
            if payment_method == 'razorpay':
                # Create Razorpay order
                order_data = {
                    'amount': int(amount * 100),  # Convert to paise
                    'currency': 'INR',
                    'receipt': f'chat_{chat_room.id}_{payment.id}',
                    'notes': {
                        'chat_id': str(chat_room.id),
                        'payment_id': str(payment.id)
                    }
                }
                
                try:
                    order = client.order.create(data=order_data)
                    payment.transaction_id = order['id']
                    payment.gateway_response = order
                    payment.save()
                    
                    return JsonResponse({
                        'success': True,
                        'order_id': order['id'],
                        'amount': order['amount'],
                        'currency': order['currency'],
                        'key_id': settings.RAZOR_KEY_ID
                    })
                except Exception as e:
                    payment.status = 'failed'
                    payment.save()
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    })
            
            elif payment_method == 'stripe':
                # Handle Stripe payment
                return JsonResponse({
                    'success': True,
                    'payment_intent': 'stripe_payment_intent_id',
                    'client_secret': 'stripe_client_secret'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Payment method not supported'
                })
    
    context = {
        'chat_room': chat_room,
        'payment_form': PaymentForm()
    }
    
    return render(request, 'chat/payment.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    """Handle payment webhooks from payment gateways"""
    
    if request.method == 'POST':
        # Verify Razorpay signature
        try:
            signature = request.headers.get('X-Razorpay-Signature')
            webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
            
            client.utility.verify_webhook_signature(
                request.body.decode(),
                signature,
                webhook_secret
            )
            
            # Process the webhook
            payload = json.loads(request.body)
            event = payload.get('event')
            
            if event == 'payment.captured':
                payment_id = payload['payload']['payment']['entity']['id']
                order_id = payload['payload']['payment']['entity']['order_id']
                
                # Update payment status
                try:
                    payment = Payment.objects.get(transaction_id=order_id)
                    payment.status = 'completed'
                    payment.gateway_response = payload
                    payment.save()
                    
                    # Update chat room payment status
                    chat_room = payment.chat_room
                    chat_room.is_paid = True
                    chat_room.payment_id = payment_id
                    chat_room.save()
                    
                    # Update vendor earnings
                    vendor = payment.vendor
                    vendor.total_earnings += payment.amount
                    vendor.save()
                    
                    # Create notification
                    from .utils import create_notification
                    create_notification(
                        user=payment.user,
                        notification_type='payment',
                        title='Payment Successful',
                        message=f'Your payment of ${payment.amount} has been processed successfully.',
                        data={'payment_id': payment.id, 'amount': str(payment.amount)}
                    )
                    
                except Payment.DoesNotExist:
                    pass
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def payment_success(request):
    """Handle successful payment redirect"""
    
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('razorpay_order_id')
    
    if payment_id and order_id:
        try:
            payment = Payment.objects.get(transaction_id=order_id)
            payment.status = 'completed'
            payment.save()
            
            # Update chat room
            chat_room = payment.chat_room
            chat_room.is_paid = True
            chat_room.payment_id = payment_id
            chat_room.save()
            
            messages.success(request, 'Payment completed successfully!')
            return redirect('chat.chat_room', chat_id=chat_room.id)
            
        except Payment.DoesNotExist:
            messages.error(request, 'Payment not found.')
    
    return redirect('chat.chat_history')

@login_required
def payment_failed(request):
    """Handle failed payment redirect"""
    
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('chat.chat_history')

@login_required
def payment_history(request):
    """Display user's payment history"""
    
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments
    }
    
    return render(request, 'chat/payment_history.html', context)

@login_required
def vendor_earnings(request):
    """Display vendor's earnings"""
    
    try:
        vendor = request.user.vendor_profile
    except:
        messages.error(request, 'Vendor profile not found.')
        return redirect('chat.vendor_registration')
    
    # Get earnings by period
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)
    
    today_earnings = Payment.objects.filter(
        vendor=vendor,
        status='completed',
        created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    week_earnings = Payment.objects.filter(
        vendor=vendor,
        status='completed',
        created_at__date__gte=this_week
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_earnings = Payment.objects.filter(
        vendor=vendor,
        status='completed',
        created_at__date__gte=this_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    recent_payments = Payment.objects.filter(
        vendor=vendor,
        status='completed'
    ).order_by('-created_at')[:10]
    
    context = {
        'vendor': vendor,
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'month_earnings': month_earnings,
        'recent_payments': recent_payments
    }
    
    return render(request, 'chat/vendor_earnings.html', context) 