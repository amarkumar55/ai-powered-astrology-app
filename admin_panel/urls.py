from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin.dashboard'),
    path('dashboard/analytics', views.analytics_dashboard, name='admin.analytics_dashboard'),

    # Users
    path('users/', views.users_list, name='admin_users'),
    path('users/<int:user_id>/', views.user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='admin_user_edit'),

    # Blogs
    path('blogs/', views.blogs_list, name='admin_blogs'),
    path('blogs/create/', views.blog_create, name='admin_blog_create'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='admin_blog_detail'),
    path('blogs/<int:blog_id>/edit/', views.blog_edit, name='admin_blog_edit'),
    path('blogs/<int:blog_id>/delete/', views.blog_delete, name='admin_blog_delete'),
    path('blogs/comments/<int:comment_id>/approve/', views.blog_comment_approve, name='admin_blog_comment_approve'),
    path('blogs/comments/<int:comment_id>/delete/', views.blog_comment_delete, name='admin_blog_comment_delete'),

    # Categories
    path('categories/', views.categories_list, name='admin_categories'),
    path('categories/create/', views.category_create, name='admin_category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='admin_category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='admin_category_delete'),

    # Kundli
    path('kundli/', views.kundli_reports, name='admin_kundli'),
    path('kundli/edit/<int:report_id>/', views.kundli_report_edit, name='kundli_report_edit'),
    
    # Horoscope
    path('horoscope/daily', views.horoscope_daily_list, name='admin_horoscope_daily'),
    path('horoscope/weekly', views.horoscope_weekly_list, name='admin_horoscope_weekly'),
    path('horoscope/monthly', views.horoscope_monthly_list, name='admin_horoscope_monthly'),
    path('horoscope/yearly', views.horoscope_yearly_list, name='admin_horoscope_yearly'),
    path('horoscope/<int:horoscope_id>/edit/', views.horoscope_edit, name='admin_horoscope_edit'),

    # Panchang
    path('panchang/', views.panchang_list, name='admin_panchang'),
    path('panchang/<int:panchang_id>/edit/', views.panchang_edit, name='admin_panchang_edit'),
    
    # Subscriptions
    path('subscriptions/', views.subscriptions, name='admin_subscription'),
    path('subscriptions/<int:subscription_id>/', views.subscription_detail, name='admin_subscription_detail'),
  
    # plans
    path('plans/', views.plans, name='admin_plans'),
    path('plans/create/', views.plan_create, name='admin_plans_create'),
    path('plans/<int:plan_id>/edit/', views.plan_edit, name='admin_plans_edit'),
    path('plans/<int:plan_id>/delete/', views.plan_delete, name='admin_plans_delete'),
    
    # invoices 
    path('invoices/', views.invoices_list, name='admin_invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='admin_invoice_detail'),
 
    # payment 
    path('payment/transactions', views.transactions_list, name='admin_transactions'),
  
    path('dasha_effect', views.dasha_effect, name='admin_dasha_effect'),
    path('dasha_effect/create', views.dasha_effect_create, name='admin_dasha_effect_create'),
    path('dasha_effect/<int:dasha_id>/edit/', views.dasha_effect_edit, name='admin_dasha_effect_edit'),
    path('dasha_effect/<int:dasha_id>/delete/', views.dasha_effect_delete, name='admin_dasha_effect_delete'),

 
    # Settings
    path('settings/', views.setting, name='admin_settings'),
    path('error_logs/', views.error_logs, name='admin_logs'),
    path('error_logs/<int:error_id>/details/', views.error_logs_details, name='admin_logs_details'),
  
    # Chatbot
    path('chatbot/', views.chatbot, name='admin_chatbot'),
    path('chatbot/send-message/', views.send_message, name='admin_chatbot_send'),
] 