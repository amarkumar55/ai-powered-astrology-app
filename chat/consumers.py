import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, Message, Vendor, VideoCall, Notification
from authentication.models import Wallet

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat room'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            sender_id = text_data_json['sender_id']
            
            # Save message to database
            saved_message = await self.save_message(message, sender_id)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'sender_name': saved_message['sender_name'],
                    'timestamp': saved_message['timestamp'],
                    'message_id': saved_message['id']
                }
            )
        
        elif message_type == 'typing':
            # Handle typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'sender_id': text_data_json['sender_id'],
                    'sender_name': text_data_json['sender_name']
                }
            )
        
        elif message_type == 'stop_typing':
            # Handle stop typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_stop_typing',
                    'sender_id': text_data_json['sender_id']
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    async def user_typing(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name']
        }))

    async def user_stop_typing(self, event):
        # Send stop typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_stop_typing',
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, message, sender_id):
        """Save message to database"""
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_id)
            sender = User.objects.get(id=sender_id)
            
            # Create message
            message_obj = Message.objects.create(
                chat_room=chat_room,
                sender=sender,
                content=message,
                message_type='text'
            )
            
            return {
                'id': message_obj.id,
                'sender_name': sender.get_full_name(),
                'timestamp': message_obj.created_at.isoformat()
            }
        except (ChatRoom.DoesNotExist, User.DoesNotExist):
            return None

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'video_call_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to video call room'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'offer':
            # Handle WebRTC offer
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'offer': text_data_json['offer'],
                    'sender_id': text_data_json['sender_id']
                }
            )
        
        elif message_type == 'answer':
            # Handle WebRTC answer
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'answer': text_data_json['answer'],
                    'sender_id': text_data_json['sender_id']
                }
            )
        
        elif message_type == 'ice_candidate':
            # Handle ICE candidate
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': text_data_json['candidate'],
                    'sender_id': text_data_json['sender_id']
                }
            )
        
        elif message_type == 'call_ring':
            # User initiates call, notify vendor
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_ringing',
                    'caller_id': text_data_json['caller_id'],
                    'caller_name': text_data_json['caller_name'],
                }
            )
        elif message_type == 'call_accept':
            # Vendor accepts call, notify both
            await self.update_call_status('connected')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_accepted',
                    'vendor_id': text_data_json['vendor_id'],
                    'vendor_name': text_data_json['vendor_name'],
                }
            )
        elif message_type == 'call_reject':
            # Vendor rejects call, notify both
            await self.update_call_status('rejected')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_rejected',
                    'vendor_id': text_data_json['vendor_id'],
                    'vendor_name': text_data_json['vendor_name'],
                }
            )
        elif message_type == 'call_started':
            # Handle call start
            await self.update_call_status('connected')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_started',
                    'sender_id': text_data_json['sender_id']
                }
            )
        
        elif message_type == 'call_ended':
            # Handle call end
            await self.update_call_status('ended')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_ended',
                    'sender_id': text_data_json['sender_id']
                }
            )
        elif message_type == 'deduct_minute':
            user_id = text_data_json.get('user_id')
            result = await self.deduct_minute(user_id)
            if not result['success']:
                # End call for both parties
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_ended',
                        'sender_id': user_id,
                        'reason': 'insufficient_balance',
                        'message': result['message'],
                    }
                )

    async def webrtc_offer(self, event):
        # Send WebRTC offer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'sender_id': event['sender_id']
        }))

    async def webrtc_answer(self, event):
        # Send WebRTC answer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'sender_id': event['sender_id']
        }))

    async def ice_candidate(self, event):
        # Send ICE candidate to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'sender_id': event['sender_id']
        }))

    async def call_ringing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_ringing',
            'caller_id': event['caller_id'],
            'caller_name': event['caller_name'],
        }))

    async def call_accepted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_accepted',
            'vendor_id': event['vendor_id'],
            'vendor_name': event['vendor_name'],
        }))

    async def call_rejected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'vendor_id': event['vendor_id'],
            'vendor_name': event['vendor_name'],
        }))

    async def call_started(self, event):
        # Send call started notification
        await self.send(text_data=json.dumps({
            'type': 'call_started',
            'sender_id': event['sender_id']
        }))

    async def call_ended(self, event):
        # Send call ended notification
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'sender_id': event['sender_id'],
            'reason': event.get('reason', ''),
            'message': event.get('message', 'Call ended.')
        }))

    @database_sync_to_async
    def update_call_status(self, status):
        """Update video call status in database"""
        try:
            video_call = VideoCall.objects.get(room_id=self.room_id)
            video_call.status = status
            if status == 'ended':
                video_call.end_time = timezone.now()
                # Calculate duration
                duration = video_call.end_time - video_call.start_time
                video_call.duration_minutes = int(duration.total_seconds() / 60)
            video_call.save()
        except VideoCall.DoesNotExist:
            pass

    @database_sync_to_async
    def deduct_minute(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            wallet = getattr(user, 'wallet', None)
            if not wallet:
                return {'success': False, 'message': 'No wallet found.'}
            if wallet.balance < 5:
                return {'success': False, 'message': 'Insufficient balance. Please top up your wallet.'}
            wallet.deduct(5)
            return {'success': True, 'message': 'Deducted 5 INR.'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

class VendorStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vendor_id = self.scope['url_route']['kwargs']['vendor_id']
        self.room_group_name = f'vendor_status_{self.vendor_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial status
        status = await self.get_vendor_status()
        await self.send(text_data=json.dumps({
            'type': 'vendor_status',
            'status': status
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'status_update':
            # Update vendor status
            is_available = text_data_json.get('is_available', False)
            await self.update_vendor_status(is_available)
            
            # Broadcast status change
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'vendor_status_update',
                    'is_available': is_available
                }
            )

    async def vendor_status_update(self, event):
        # Send status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'vendor_status_update',
            'is_available': event['is_available']
        }))

    @database_sync_to_async
    def get_vendor_status(self):
        """Get current vendor status"""
        try:
            vendor = Vendor.objects.get(id=self.vendor_id)
            return {
                'vendor_id': vendor.id,
                'is_available': vendor.is_available,
                'status': vendor.status,
                'hourly_rate': str(vendor.hourly_rate)
            }
        except Vendor.DoesNotExist:
            return None

    @database_sync_to_async
    def update_vendor_status(self, is_available):
        """Update vendor availability status"""
        try:
            vendor = Vendor.objects.get(id=self.vendor_id)
            vendor.is_available = is_available
            vendor.save()
        except Vendor.DoesNotExist:
            pass

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'user_notifications_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle any incoming messages if needed
        pass

    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'notification_type': event['notification_type']
        }))

    async def chat_notification(self, event):
        # Send chat notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_notification',
            'chat_id': event['chat_id'],
            'sender_name': event['sender_name'],
            'message_preview': event['message_preview']
        }))

    async def video_call_notification(self, event):
        # Send video call notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'video_call_notification',
            'call_id': event['call_id'],
            'caller_name': event['caller_name'],
            'room_id': event['room_id']
        }))

    async def payment_notification(self, event):
        # Send payment notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'payment_notification',
            'payment_id': event['payment_id'],
            'amount': event['amount'],
            'status': event['status']
        })) 