from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from chat.models import Notification
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Device
from django.utils import timezone

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Optional: mark as read automatically
        if not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=["is_read","read_at"])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'All notifications marked as read.'})



class SaveFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("fcm_token")
        if not token:
            return Response({"error": "FCM token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save or update the token
        Device.objects.update_or_create(
            user=request.user,
            defaults={"fcm_token": token}
        )

        return Response({"message": "Token saved successfully."}, status=status.HTTP_200_OK)