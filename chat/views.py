import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Vendor, ChatRoom, Message, VendorAvailability, ChatSession, VideoCall
from .forms import (
    VendorRegistrationForm, VendorSearchForm, ChatRoomForm, 
    MessageForm, VendorReviewForm, VendorProfileUpdateForm
)
from utlity.helper import store_activity
from .utils import create_video_call
from authentication.models import Wallet
from .utils import create_notification

User = get_user_model()

@login_required
def vendor_list(request):
    """Display list of available vendors/consultants"""
    
    # Get search parameters
    form = VendorSearchForm(request.GET)
    vendors = Vendor.objects.filter(status='approved', is_available=True)
    
    if form.is_valid():
        specialization = form.cleaned_data.get('specialization')
        max_rate = form.cleaned_data.get('max_rate')
        rating_min = form.cleaned_data.get('rating_min')
        available_now = form.cleaned_data.get('available_now')
        
        if specialization:
            vendors = vendors.filter(specialization=specialization)
        
        if max_rate:
            vendors = vendors.filter(hourly_rate__lte=max_rate)
        
        if rating_min:
            vendors = vendors.filter(rating__gte=rating_min)
        
        if available_now:
            # Filter for vendors available right now
            current_time = timezone.now().time()
            current_day = timezone.now().weekday()
            vendors = vendors.filter(
                availability_slots__day_of_week=current_day,
                availability_slots__start_time__lte=current_time,
                availability_slots__end_time__gte=current_time,
                availability_slots__is_available=True
            )
    
    # Order by featured first, then rating
    vendors = vendors.order_by('-is_featured', '-rating')
    
    # Pagination
    paginator = Paginator(vendors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vendors': page_obj,
        'search_form': form,
        'specializations': Vendor.SPECIALIZATION_CHOICES,
    }
    
    return render(request, 'chat/vendor_list.html', context)

@login_required
def vendor_detail(request, vendor_id):
    """Display detailed vendor profile"""
    
    vendor = get_object_or_404(Vendor, id=vendor_id, status='approved')
    
    # Get vendor's recent reviews
    recent_chats = ChatRoom.objects.filter(
        vendor=vendor,
        rating__isnull=False
    ).order_by('-created_at')[:5]
    
    # Check if user has an active chat with this vendor
    active_chat = ChatRoom.objects.filter(
        user=request.user,
        vendor=vendor,
        status='active'
    ).first()
    
    context = {
        'vendor': vendor,
        'recent_chats': recent_chats,
        'active_chat': active_chat,
    }
    
    return render(request, 'chat/vendor_detail.html', context)

@login_required
def vendor_registration(request):
    """Allow users to register as vendors"""
    
    if hasattr(request.user, 'vendor_profile'):
        messages.warning(request, 'You are already registered as a vendor.')
        return redirect('chat.vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            
            messages.success(request, 'Your vendor application has been submitted for approval.')
            return redirect('chat.vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    
    context = {
        'form': form,
        'specializations': Vendor.SPECIALIZATION_CHOICES,
    }
    
    return render(request, 'chat/vendor_registration.html', context)

@login_required
def vendor_dashboard(request):
    """Dashboard for vendors to manage their profile and chats"""
    
    try:
        vendor = request.user.vendor_profile
    except Vendor.DoesNotExist:
        messages.warning(request, 'You need to register as a vendor first.')
        return redirect('chat.vendor_registration')
    
    # Get vendor's active chats
    active_chats = ChatRoom.objects.filter(
        vendor=vendor,
        status='active'
    ).order_by('-start_time')
    
    # Get recent completed chats
    recent_chats = ChatRoom.objects.filter(
        vendor=vendor,
        status='ended'
    ).order_by('-end_time')[:10]
    
    # Get today's earnings
    today = timezone.now().date()
    today_earnings = ChatRoom.objects.filter(
        vendor=vendor,
        end_time__date=today,
        is_paid=True
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    context = {
        'vendor': vendor,
        'active_chats': active_chats,
        'recent_chats': recent_chats,
        'today_earnings': today_earnings,
    }
    
    return render(request, 'chat/vendor_dashboard.html', context)

@login_required
def vendor_profile_edit(request):
    """Allow vendors to edit their profile"""
    
    try:
        vendor = request.user.vendor_profile
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found.')
        return redirect('chat.vendor_registration')
    
    if request.method == 'POST':
        form = VendorProfileUpdateForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('chat.vendor_dashboard')
    else:
        form = VendorProfileUpdateForm(instance=vendor)
    
    context = {
        'form': form,
        'vendor': vendor,
    }
    
    return render(request, 'chat/vendor_profile_edit.html', context)

@login_required
def start_chat(request, vendor_id):
    """Start a new chat session with a vendor"""
    
    vendor = get_object_or_404(Vendor, id=vendor_id, status='approved', is_available=True)
    
    # Check if user already has an active chat with this vendor
    existing_chat = ChatRoom.objects.filter(
        user=request.user,
        vendor=vendor,
        status='active'
    ).first()
    
    if existing_chat:
        return redirect('chat.chat_room', chat_id=existing_chat.id)
    
    # Create new chat room
    chat_room = ChatRoom.objects.create(
        user=request.user,
        vendor=vendor,
        status='active'
    )
    
    # Create initial system message
    Message.objects.create(
        chat_room=chat_room,
        sender=request.user,
        message_type='system',
        content=f'Chat session started with {vendor.full_name}'
    )
    
    # Store activity
    store_activity(
        user=request.user,
        activity_type='chat_started',
        data={'vendor_id': vendor.id, 'chat_id': chat_room.id},
        ip_address=request.META.get('REMOTE_ADDR', ''),
        browser=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return redirect('chat.chat_room', chat_id=chat_room.id)

@login_required
def chat_room(request, chat_id):
    """Display chat room interface"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id)
    
    # Check if user has access to this chat
    if request.user not in [chat_room.user, chat_room.vendor.user]:
        messages.error(request, 'You do not have access to this chat.')
        return redirect('chat.vendor_list')
    
    # Get messages for this chat
    messages_list = chat_room.messages.all().order_by('created_at')
    
    # Mark messages as read
    unread_messages = messages_list.filter(
        is_read=False
    ).exclude(sender=request.user)
    unread_messages.update(is_read=True, read_at=timezone.now())
    
    context = {
        'chat_room': chat_room,
        'messages': messages_list,
        'message_form': MessageForm(),
    }
    
    return render(request, 'chat/chat_room.html', context)

@login_required
@require_http_methods(["POST"])
def send_message(request, chat_id):
    """Send a message in the chat room"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id)
    
    # Check if user has access to this chat
    if request.user not in [chat_room.user, chat_room.vendor.user]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Check if chat is active
    if chat_room.status != 'active':
        return JsonResponse({'error': 'Chat is not active'}, status=400)
    
    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        message = form.save(commit=False)
        message.chat_room = chat_room
        message.sender = request.user
        
        if request.FILES.get('file'):
            message.message_type = 'file'
        
        message.save()
        
        # Store activity
        store_activity(
            user=request.user,
            activity_type='message_sent',
            data={'chat_id': chat_room.id, 'message_id': message.id},
            ip_address=request.META.get('REMOTE_ADDR', ''),
            browser=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'content': message.content,
            'sender_name': message.sender.get_full_name(),
            'timestamp': message.created_at.isoformat(),
        })
    
    return JsonResponse({'error': 'Invalid message'}, status=400)

@login_required
def end_chat(request, chat_id):
    """End a chat session"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id)
    
    # Check if user has access to this chat
    if request.user not in [chat_room.user, chat_room.vendor.user]:
        messages.error(request, 'You do not have access to this chat.')
        return redirect('chat.vendor_list')
    
    if chat_room.status == 'active':
        chat_room.status = 'ended'
        chat_room.end_time = timezone.now()
        
        # Calculate duration
        duration = chat_room.end_time - chat_room.start_time
        chat_room.duration_minutes = int(duration.total_seconds() / 60)
        
        # Calculate cost (hourly rate / 60 * duration in minutes)
        hourly_rate = chat_room.vendor.hourly_rate
        chat_room.total_cost = (hourly_rate / 60) * chat_room.duration_minutes
        
        chat_room.save()
        
        # Create system message
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type='system',
            content=f'Chat session ended. Duration: {chat_room.duration_formatted}, Cost: ${chat_room.total_cost:.2f}'
        )
        
        messages.success(request, 'Chat session ended successfully.')
    
    return redirect('chat.chat_history')

@login_required
def chat_history(request):
    """Display user's chat history"""
    
    if hasattr(request.user, 'vendor_profile'):
        # Vendor view - show chats where they are the vendor
        chats = ChatRoom.objects.filter(vendor=request.user.vendor_profile)
    else:
        # User view - show chats where they are the user
        chats = ChatRoom.objects.filter(user=request.user)
    
    chats = chats.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(chats, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'chats': page_obj,
        'is_vendor': hasattr(request.user, 'vendor_profile'),
    }
    
    return render(request, 'chat/chat_history.html', context)

@login_required
def review_vendor(request, chat_id):
    """Review a vendor after chat session"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id, user=request.user, status='ended')
    
    if chat_room.rating:
        messages.warning(request, 'You have already reviewed this vendor.')
        return redirect('chat.chat_history')
    
    if request.method == 'POST':
        form = VendorReviewForm(request.POST)
        if form.is_valid():
            chat_room.rating = form.cleaned_data['rating']
            chat_room.review = form.cleaned_data['review']
            chat_room.save()
            
            # Update vendor's average rating
            vendor = chat_room.vendor
            avg_rating = ChatRoom.objects.filter(
                vendor=vendor,
                rating__isnull=False
            ).aggregate(avg=Avg('rating'))['avg']
            
            if avg_rating:
                vendor.rating = round(avg_rating, 2)
                vendor.save()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('chat.chat_history')
    else:
        form = VendorReviewForm()
    
    context = {
        'form': form,
        'chat_room': chat_room,
    }
    
    return render(request, 'chat/review_vendor.html', context)

# API endpoints for real-time chat
@login_required
@csrf_exempt
def get_messages(request, chat_id):
    """Get messages for a chat room (API endpoint)"""
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id)
    
    # Check if user has access to this chat
    if request.user not in [chat_room.user, chat_room.vendor.user]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    messages = chat_room.messages.all().order_by('created_at')
    
    # Mark messages as read
    unread_messages = messages.filter(
        is_read=False
    ).exclude(sender=request.user)
    unread_messages.update(is_read=True, read_at=timezone.now())
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name(),
            'message_type': msg.message_type,
            'is_read': msg.is_read,
            'timestamp': msg.created_at.isoformat(),
            'file_url': msg.file.url if msg.file else None,
        })
    
    return JsonResponse({'messages': messages_data})

@login_required
@csrf_exempt
def get_vendor_status(request, vendor_id):
    """Get vendor's current availability status (API endpoint)"""
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Check if vendor is currently available
    current_time = timezone.now().time()
    current_day = timezone.now().weekday()
    
    is_available_now = VendorAvailability.objects.filter(
        vendor=vendor,
        day_of_week=current_day,
        start_time__lte=current_time,
        end_time__gte=current_time,
        is_available=True
    ).exists()
    
    return JsonResponse({
        'vendor_id': vendor.id,
        'is_available': vendor.is_available and is_available_now,
        'status': vendor.status,
        'hourly_rate': str(vendor.hourly_rate),
    })

@login_required
def video_call_room(request, chat_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_id)
    user = request.user
    # Only allow chat participants
    if user != chat_room.user and user != chat_room.vendor.user:
        return HttpResponseForbidden("You are not a participant in this chat.")

    # Only users (not vendors) need wallet check to initiate
    is_user = (user == chat_room.user)
    wallet = getattr(user, 'wallet', None)
    min_balance = 5.0
    if is_user and (not wallet or wallet.balance < min_balance):
        return render(request, 'chat/insufficient_balance.html', {
            'required': min_balance,
            'balance': wallet.balance if wallet else 0,
        })

    # Find or create a VideoCall for this chat
    video_call = VideoCall.objects.filter(chat_room=chat_room, status__in=["initiated", "ringing", "connected"]).first()
    is_initiator = False
    if not video_call:
        # The first user to access becomes the initiator
        video_call = create_video_call(chat_room, user)
        is_initiator = True
    else:
        is_initiator = (video_call.initiator == user)

    context = {
        'room_id': video_call.room_id,
        'is_initiator': is_initiator,
        'chat_room': chat_room,
    }
    return render(request, 'chat/video_call.html', context)

@login_required
def video_call_history(request):
    user = request.user
    # Show all calls where the user is a participant (as user or vendor)
    calls = VideoCall.objects.filter(
        chat_room__user=user
    ) | VideoCall.objects.filter(
        chat_room__vendor__user=user
    )
    calls = calls.select_related('chat_room', 'chat_room__vendor', 'chat_room__user').order_by('-start_time')
    context = {
        'calls': calls,
    }
    return render(request, 'chat/video_call_history.html', context)

@csrf_exempt
@login_required
def video_call_rate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            rating = int(data.get('rating'))
            review = data.get('review', '')
            # Find the VideoCall by room_id
            call = VideoCall.objects.filter(room_id=room_id).order_by('-start_time').first()
            if not call:
                return JsonResponse({'success': False, 'error': 'Call not found.'})
            # Only the user who participated can rate
            if request.user != call.chat_room.user:
                return JsonResponse({'success': False, 'error': 'Permission denied.'})
            call.rating = rating
            call.review = review
            call.save()
            # Notify vendor
            create_notification(
                user=call.chat_room.vendor.user,
                notification_type='system',
                title='New Video Call Review',
                message=f'You received a new review: {rating}/5. "{review}"',
                data={'call_id': call.id, 'rating': rating, 'review': review}
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})
