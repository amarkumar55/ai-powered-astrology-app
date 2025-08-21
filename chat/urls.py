from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Vendor listing and search
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:vendor_id>/status/', views.get_vendor_status, name='vendor_status'),
    
    # Vendor registration and management
    path('vendor/register/', views.vendor_registration, name='vendor_registration'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/profile/edit/', views.vendor_profile_edit, name='vendor_profile_edit'),
    
    # Chat functionality
    path('start-chat/<int:vendor_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:chat_id>/end/', views.end_chat, name='end_chat'),
    path('chat/<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    
    # Chat history and reviews
    path('chat-history/', views.chat_history, name='chat_history'),
    path('chat/<int:chat_id>/review/', views.review_vendor, name='review_vendor'),
    path('video-call/<int:chat_id>/', views.video_call_room, name='video_call_room'),
    path('video-call-history/', views.video_call_history, name='video_call_history'),
    path('video-call/rate/', views.video_call_rate, name='video_call_rate'),
] 