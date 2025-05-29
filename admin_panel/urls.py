from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),

    # Users
    path('users/', views.users_list, name='admin_users'),
    path('users/<int:user_id>/', views.user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='admin_user_edit'),

    # Blogs
    path('blogs/', views.blogs_list, name='admin_blogs'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='admin_blog_detail'),
    path('blogs/<int:blog_id>/edit/', views.blog_edit, name='admin_blog_edit'),

    # Kundli
    path('kundli/', views.kundli_list, name='admin_kundli'),
    path('kundli/<int:kundli_id>/', views.kundli_detail, name='admin_kundli_detail'),
    path('kundli/<int:kundli_id>/ai-analysis/', views.analyze_kundli_ai, name='admin_kundli_ai_analysis'),

    # Horoscope
    path('horoscope/', views.horoscope_list, name='admin_horoscope'),
    path('horoscope/<int:horoscope_id>/edit/', views.horoscope_edit, name='admin_horoscope_edit'),

    # Panchang
    path('panchang/', views.panchang_list, name='admin_panchang'),
    path('panchang/<int:panchang_id>/edit/', views.panchang_edit, name='admin_panchang_edit'),

    # Subscriptions
    path('subscriptions/', views.subscription_list, name='admin_subscription'),
    path('subscriptions/<int:subscription_id>/', views.subscription_detail, name='admin_subscription_detail'),

    # Settings
    path('settings/', views.settings, name='admin_settings'),

    # Analytics
    path('analytics/', views.analytics_dashboard, name='admin_analytics'),

    # Chatbot
    path('chatbot/', views.chatbot, name='admin_chatbot'),
    path('chatbot/send-message/', views.send_message, name='admin_chatbot_send'),
] 