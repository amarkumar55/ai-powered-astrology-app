from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, VideoCall
import uuid

def create_notification(user, notification_type, title, message, data=None):
    """Create a notification for a user"""
    
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {}
    )
    
    # Send real-time notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_notifications_{user.id}',
        {
            'type': 'notification_message',
            'message': message,
            'notification_type': notification_type
        }
    )
    
    return notification

def create_video_call_notification(user, caller_name, room_id):
    """Create a video call notification"""
    
    notification = create_notification(
        user=user,
        notification_type='video_call',
        title='Incoming Video Call',
        message=f'{caller_name} is calling you',
        data={'room_id': room_id, 'caller_name': caller_name}
    )
    
    # Send real-time video call notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_notifications_{user.id}',
        {
            'type': 'video_call_notification',
            'call_id': notification.id,
            'caller_name': caller_name,
            'room_id': room_id
        }
    )
    
    return notification

def create_payment_notification(user, payment_id, amount, status):
    """Create a payment notification"""
    
    notification = create_notification(
        user=user,
        notification_type='payment',
        title='Payment Update',
        message=f'Payment of ${amount} is {status}',
        data={'payment_id': payment_id, 'amount': amount, 'status': status}
    )
    
    # Send real-time payment notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_notifications_{user.id}',
        {
            'type': 'payment_notification',
            'payment_id': payment_id,
            'amount': amount,
            'status': status
        }
    )
    
    return notification

def generate_room_id():
    """Generate a unique room ID for video calls"""
    return str(uuid.uuid4())

def create_video_call(chat_room, initiator):
    """Create a new video call session"""
    
    room_id = generate_room_id()
    
    video_call = VideoCall.objects.create(
        chat_room=chat_room,
        initiator=initiator,
        room_id=room_id,
        status='initiated'
    )
    
    return video_call

def get_user_notifications(user, limit=10):
    """Get user's recent notifications"""
    return Notification.objects.filter(user=user).order_by('-created_at')[:limit]

def mark_notification_read(notification_id, user):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False

def mark_all_notifications_read(user):
    """Mark all user notifications as read"""
    unread_notifications = Notification.objects.filter(user=user, is_read=False)
    unread_notifications.update(is_read=True, read_at=timezone.now())
    return unread_notifications.count()

def get_unread_notification_count(user):
    """Get count of unread notifications for a user"""
    return Notification.objects.filter(user=user, is_read=False).count()

def send_chat_notification(chat_room, sender, message_preview):
    """Send real-time chat notification"""
    
    # Determine recipient
    if sender == chat_room.user:
        recipient = chat_room.vendor.user
        sender_name = chat_room.user.get_full_name()
    else:
        recipient = chat_room.user
        sender_name = chat_room.vendor.full_name
    
    # Create notification
    notification = create_notification(
        user=recipient,
        notification_type='chat_message',
        title='New Message',
        message=f'{sender_name}: {message_preview}',
        data={'chat_id': chat_room.id, 'sender_name': sender_name}
    )
    
    # Send real-time notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_notifications_{recipient.id}',
        {
            'type': 'chat_notification',
            'chat_id': chat_room.id,
            'sender_name': sender_name,
            'message_preview': message_preview
        }
    )
    
    return notification

def update_vendor_availability(vendor, is_available):
    """Update vendor availability status"""
    
    vendor.is_available = is_available
    vendor.save()
    
    # Send real-time status update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'vendor_status_{vendor.id}',
        {
            'type': 'vendor_status_update',
            'is_available': is_available
        }
    )
    
    return vendor

def calculate_chat_cost(chat_room):
    """Calculate the cost of a chat session"""
    
    if not chat_room.end_time:
        return 0.00
    
    duration = chat_room.end_time - chat_room.start_time
    duration_minutes = duration.total_seconds() / 60
    
    hourly_rate = chat_room.vendor.hourly_rate
    cost = (hourly_rate / 60) * duration_minutes
    
    return round(cost, 2)

def format_duration(minutes):
    """Format duration in a human-readable format"""
    
    if minutes < 60:
        return f"{int(minutes)}m"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {mins}m"

def get_vendor_stats(vendor):
    """Get comprehensive vendor statistics"""
    
    from django.db.models import Avg, Count, Sum
    from datetime import timedelta
    
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)
    
    # Chat statistics
    total_chats = ChatRoom.objects.filter(vendor=vendor).count()
    active_chats = ChatRoom.objects.filter(vendor=vendor, status='active').count()
    completed_chats = ChatRoom.objects.filter(vendor=vendor, status='ended').count()
    
    # Payment statistics
    total_earnings = Payment.objects.filter(
        vendor=vendor, 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    today_earnings = Payment.objects.filter(
        vendor=vendor,
        status='completed',
        created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Rating statistics
    avg_rating = ChatRoom.objects.filter(
        vendor=vendor,
        rating__isnull=False
    ).aggregate(avg=Avg('rating'))['avg'] or 0
    
    total_ratings = ChatRoom.objects.filter(
        vendor=vendor,
        rating__isnull=False
    ).count()
    
    # Video call statistics
    total_video_calls = VideoCall.objects.filter(chat_room__vendor=vendor).count()
    completed_video_calls = VideoCall.objects.filter(
        chat_room__vendor=vendor,
        status='ended'
    ).count()
    
    return {
        'total_chats': total_chats,
        'active_chats': active_chats,
        'completed_chats': completed_chats,
        'total_earnings': total_earnings,
        'today_earnings': today_earnings,
        'avg_rating': round(avg_rating, 1),
        'total_ratings': total_ratings,
        'total_video_calls': total_video_calls,
        'completed_video_calls': completed_video_calls
    } 