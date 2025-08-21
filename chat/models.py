from django.db import models
from django.contrib.auth import get_user_model
from home.models import TimeStampMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()

class Vendor(TimeStampMixin):
    """Model for vendors/consultants (astrologers, tarot readers, etc.)"""
    
    SPECIALIZATION_CHOICES = [
        ('astrologer', 'Astrologer'),
        ('tarot_reader', 'Tarot Card Reader'),
        ('numerologist', 'Numerologist'),
        ('palmist', 'Palmist'),
        ('vastu_expert', 'Vastu Expert'),
        ('crystal_healer', 'Crystal Healer'),
        ('reiki_master', 'Reiki Master'),
        ('meditation_guide', 'Meditation Guide'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    experience_years = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    bio = models.TextField(max_length=1000)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sessions = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_image = models.ImageField(upload_to='vendors/profiles/', blank=True, null=True)
    certificates = models.FileField(upload_to='vendors/certificates/', blank=True, null=True)
    languages = models.JSONField(default=list, blank=True)  # List of languages spoken
    consultation_hours = models.JSONField(default=dict, blank=True)  # Available hours
    is_featured = models.BooleanField(default=False)
    supports_video_call = models.BooleanField(default=True)  # New field for video support
    
    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        app_label = "astrology"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email

    @property
    def video_calls_received(self):
        from chat.models import VideoCall
        return VideoCall.objects.filter(chat_room__vendor=self)

    @property
    def aggregate_avg_rating(self):
        from django.db.models import Avg
        return self.vendor_chats.filter(video_calls__rating__isnull=False).aggregate(avg=Avg('video_calls__rating'))['avg']

    @property
    def recent_reviews(self):
        from chat.models import VideoCall
        return VideoCall.objects.filter(chat_room__vendor=self, rating__isnull=False).order_by('-start_time')[:5]

class ChatRoom(TimeStampMixin):
    """Model for chat rooms between users and vendors"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chats')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_chats')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"
        unique_together = ['user', 'vendor', 'start_time']
    
    def __str__(self):
        return f"Chat: {self.user.get_full_name()} with {self.vendor.full_name}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def duration_formatted(self):
        if self.duration_minutes:
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "0m"

class Message(TimeStampMixin):
    """Model for individual messages in chat rooms"""
    
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    file = models.FileField(upload_to='chat/files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} in {self.chat_room}"
    
    @property
    def is_from_vendor(self):
        return self.sender == self.chat_room.vendor.user
    
    @property
    def is_from_user(self):
        return self.sender == self.chat_room.user

class VideoCall(TimeStampMixin):
    """Model for video call sessions"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('connected', 'Connected'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected'),
    ]
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='video_calls')
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_calls')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    room_id = models.CharField(max_length=100, unique=True)  # WebRTC room ID
    session_id = models.CharField(max_length=100, blank=True, null=True)  # For TURN server
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Video Call"
        verbose_name_plural = "Video Calls"
    
    def __str__(self):
        return f"Video Call: {self.chat_room} - {self.status}"

class Notification(TimeStampMixin):
    """Model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('chat_message', 'Chat Message'),
        ('video_call', 'Video Call'),
        ('payment', 'Payment'),
        ('system', 'System'),
        ('vendor_approval', 'Vendor Approval'),
        ('app', 'App'),
        ('email', 'Email'),
        ('promotion', 'Promotion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    data = models.JSONField(default=dict, blank=True)  # Additional data (chat_id, vendor_id, etc.)
    
    class Meta:
        app_label = "core"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.get_full_name()}: {self.title}"

class VendorPaymentHistroy(TimeStampMixin):
    """Model for payment transactions"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_payment_histories')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='received_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Vendor Payment"
        verbose_name_plural = "Vendor Payments"
    
    def __str__(self):
        return f"Payment: {self.user.get_full_name()} to {self.vendor.full_name} - ${self.amount}"



class VendorAvailability(TimeStampMixin):
    """Model to track vendor availability schedules"""
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.PositiveIntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Vendor Availability"
        verbose_name_plural = "Vendor Availabilities"
        unique_together = ['vendor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.vendor.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class ChatSession(TimeStampMixin):
    """Model to track individual chat sessions for billing"""
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_billed = models.BooleanField(default=False)
    
    class Meta:
        app_label = "astrology"
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
    
    def __str__(self):
        return f"Session: {self.chat_room} - {self.start_time}"
