from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from payment.models import Payment, Refund
from .serializers import PaymentSerializer, RefundSerializer
from rest_framework.pagination import PageNumberPagination

class PaymentListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class RefundListPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 100

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaymentListPagination
    def get_queryset(self):
        return Payment.objects.using(self.request.db).filter(user=self.request.user).order_by('-created_at')

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Payment.objects.using(self.request.db).filter(user=self.request.user)
    lookup_field = 'id'

class PaymentProcessView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # Example: expects amount, payment_method, description
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        description = request.data.get('description', '')
        currency = request.data.get('currency', 'INR')
        # Here you would integrate with Razorpay/Stripe/PayPal SDKs
        # For now, just create a pending Payment record
        payment = Payment.objects.using(self.request.db).create(
            user=request.user,
            amount=amount,
            currency=currency,
            status='pending',
            payment_method=payment_method,
            description=description
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

class RefundListView(generics.ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = RefundListPagination
    def get_queryset(self):
        return Refund.objects.using(self.request.db).filter(payment__user=self.request.user).order_by('-created_at')

class RefundDetailView(generics.RetrieveAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Refund.objects.using(self.request.db).filter(payment__user=self.request.user)
    lookup_field = 'id' 