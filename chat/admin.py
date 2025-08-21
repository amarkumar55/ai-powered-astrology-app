from django.contrib import admin
from .models import Vendor, ChatRoom, Message, VendorAvailability, ChatSession, VideoCall, Notification, Payment

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'status', 'is_available', 'rating', 'hourly_rate', 'total_sessions', 'supports_video_call']
    list_filter = ['status', 'specialization', 'is_available', 'is_featured', 'supports_video_call', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio']
    readonly_fields = ['rating', 'total_sessions', 'total_earnings', 'created_at', 'updated_at']
    list_editable = ['status', 'is_available', 'is_featured', 'supports_video_call']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'specialization', 'bio', 'experience_years')
        }),
        ('Business Details', {
            'fields': ('hourly_rate', 'languages', 'consultation_hours', 'is_available', 'supports_video_call')
        }),
        ('Status & Approval', {
            'fields': ('status', 'is_featured')
        }),
        ('Performance', {
            'fields': ('rating', 'total_sessions', 'total_earnings'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('profile_image', 'certificates'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['user', 'vendor', 'status', 'start_time', 'duration_formatted', 'total_cost', 'is_paid']
    list_filter = ['status', 'is_paid', 'start_time', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'vendor__user__first_name', 'vendor__user__last_name']
    readonly_fields = ['start_time', 'end_time', 'duration_minutes', 'total_cost', 'created_at', 'updated_at']
    list_editable = ['status', 'is_paid']
    
    fieldsets = (
        ('Chat Information', {
            'fields': ('user', 'vendor', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Payment', {
            'fields': ('total_cost', 'is_paid', 'payment_id')
        }),
        ('Feedback', {
            'fields': ('rating', 'review'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'chat_room', 'message_type', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'sender__first_name', 'sender__last_name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_read']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('chat_room', 'sender', 'message_type', 'content')
        }),
        ('File Attachment', {
            'fields': ('file',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VideoCall)
class VideoCallAdmin(admin.ModelAdmin):
    list_display = ['chat_room', 'initiator', 'status', 'start_time', 'duration_minutes', 'room_id']
    list_filter = ['status', 'start_time', 'created_at']
    search_fields = ['room_id', 'session_id', 'initiator__first_name', 'initiator__last_name']
    readonly_fields = ['start_time', 'end_time', 'duration_minutes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Call Information', {
            'fields': ('chat_room', 'initiator', 'status', 'room_id', 'session_id')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'vendor', 'amount', 'currency', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'user__first_name', 'vendor__user__first_name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('chat_room', 'user', 'vendor', 'amount', 'currency', 'payment_method')
        }),
        ('Status & Transaction', {
            'fields': ('status', 'transaction_id', 'description')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VendorAvailability)
class VendorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'created_at']
    search_fields = ['vendor__user__first_name', 'vendor__user__last_name']
    list_editable = ['is_available']
    
    fieldsets = (
        ('Availability Details', {
            'fields': ('vendor', 'day_of_week', 'start_time', 'end_time', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['chat_room', 'start_time', 'end_time', 'duration_minutes', 'cost', 'is_billed']
    list_filter = ['is_billed', 'start_time', 'created_at']
    search_fields = ['chat_room__user__first_name', 'chat_room__vendor__user__first_name']
    readonly_fields = ['start_time', 'end_time', 'duration_minutes', 'cost', 'created_at', 'updated_at']
    list_editable = ['is_billed']
    
    fieldsets = (
        ('Session Details', {
            'fields': ('chat_room', 'start_time', 'end_time')
        }),
        ('Billing', {
            'fields': ('duration_minutes', 'cost', 'is_billed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
