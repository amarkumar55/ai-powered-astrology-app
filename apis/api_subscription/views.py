from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from subscription.models import Plan, UserSubscription
from .serializers import PlanSerializer, UserSubscriptionSerializer
from invoice.models import Invoice
from invoice.utlity import create_invoice
from django.utils import timezone
import razorpay
from django.conf import settings
from authentication.models import Wallet
from rest_framework.permissions import IsAuthenticated
from payment.models import Payment
from rest_framework.pagination import PageNumberPagination
from authentication.models import WalletTransaction
from utlity.helper import store_activity
from django.core.mail import send_mail
class PlanListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class UserAstrologySubscriptionsPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PlanListPagination

    def get_queryset(self):
        return Plan.objects.using(self.request.db).filter(is_active=True).order_by('id')
    
class PlanDetailView(generics.RetrieveAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


    def get_queryset(self):
        return Plan.objects.using(self.request.db)
   
    lookup_field = 'slug'

class UserAstrologySubscriptionsView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserAstrologySubscriptionsPagination

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user).order_by('-start_date') 
    
class SubscribeAstroPlanView(APIView):
  
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_slug = request.data.get('plan_slug')
        plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
        user = request.user
        # Set end_date based on plan duration
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=plan.duration_days)
        # Create subscription
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='active',
            payment_paid=False
        )
       
        # Create invoice
        invoice = create_invoice(plan, user, user.get_full_name(), user.email, "")
        invoice.subscription = subscription
        invoice.save()
        subscription.invoice_id = invoice.id
        subscription.save()

        return Response({
            'subscription': UserSubscriptionSerializer(subscription).data,
            'invoice_id': invoice.id
        }, status=status.HTTP_201_CREATED)



class RazorpayCheckoutView(APIView):
  
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        plan = get_object_or_404(Plan.objects.using(request.db), id=plan_id, is_active=True)
        user = request.user
        amount = int(float(plan.price) * 100)  # Razorpay expects paise
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'subscription_{plan.id}_{user.id}',
            'notes': {
                'plan_id': str(plan.id),
                'user_id': str(user.id)
            }
        }
        order = client.order.create(data=order_data)
    
        return Response({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZOR_KEY_ID,  # match frontend expectation
            'email': user.email,
            'contact': user.profile.cell if hasattr(user, 'profile') else "",
            'name': f'{user.first_name} {user.last_name}',
            'plan': PlanSerializer(plan).data
        }, status=status.HTTP_200_OK)
            
    
from django.db import transaction

class AssignPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get('plan_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')

        plan = get_object_or_404(
            Plan.objects.using(request.db), id=plan_id, is_active=True
        )
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # 1️⃣ Verify payment signature first (before transaction)
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception as e:
            return Response(
                {'error': 'Payment verification failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Start atomic transaction
        try:
            with transaction.atomic(using=request.db):
                wallet, _ = Wallet.objects.using(request.db).get_or_create(user=user)
                wallet.balance += plan.duration_days
            
                wallet.save()

                payment_obj = client.payment.fetch(razorpay_payment_id)
                currency = payment_obj.get('currency', 'INR')
                payment_status = (
                    'success' if payment_obj.get('status') == 'captured' else payment_obj.get('status')
                )
                payment_method = payment_obj.get('method', 'razorpay')

                WalletTransaction.objects.using(request.db).create(
                    transaction_type='credit',
                    wallet=wallet,
                    amount=plan.duration_days,
                    description=f"Recharged wallet with {plan.name}"
                )

                Payment.objects.using(request.db).create(
                    user=request.user,
                    amount=plan.price,
                    currency=currency,
                    status=payment_status,
                    payment_method=payment_method,
                    payment_id=razorpay_payment_id,
                    order_id=razorpay_order_id,
                    description=f'{plan.duration_days} tokens credited into your wallet',
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                store_activity(request, {}, f"Recharged Wallet with plan {plan.name}" ,request.user)
            
                send_mail(
                    subject="Wallet Recharge Successful",
                    message=(
                        f"Hello {user.first_name or user.username},\n\n"
                        f"Your wallet has been successfully recharged with the '{plan.name}' plan.\n"
                        f"Credits Added: {plan.duration_days} tokens\n"
                        f"Updated Wallet Balance: {wallet.balance} tokens\n\n"
                        "Thank you for choosing our service!\n"
                        "If you have any questions, feel free to reply to this email.\n\n"
                        "Best regards,\n"
                        "The NoteWise Team"
                    ),
                    from_email='noreply@yourdomain.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Something went wrong', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
