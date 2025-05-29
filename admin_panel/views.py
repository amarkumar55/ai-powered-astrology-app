from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import openai
from django.conf import settings
from django.contrib import messages

# Create your views here.

def analytics_dashboard(request):
    if not is_admin(request.user):
        return redirect('login')
    
    # Get date range for analytics (last 6 months)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=180)
    
    # User statistics
    total_users = CustomUser.objects.count()
    new_users_this_month = CustomUser.objects.filter(
        date_joined__gte=start_date
    ).count()
    user_growth = round((new_users_this_month / total_users * 100) if total_users > 0 else 0, 1)
    
    # User growth data for chart
    user_growth_data = CustomUser.objects.annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    user_growth_labels = [data['month'].strftime('%B %Y') for data in user_growth_data]
    user_growth_data = [data['count'] for data in user_growth_data]
    
    # Subscription statistics
    active_subscriptions = UserSubscription.objects.filter(
        status='active'
    ).count()
    new_subscriptions_this_month = UserSubscription.objects.filter(
        created_at__gte=start_date
    ).count()
    subscription_growth = round((new_subscriptions_this_month / active_subscriptions * 100) if active_subscriptions > 0 else 0, 1)
    
    # Subscription distribution data
    subscription_data = UserSubscription.objects.values(
        'plan__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    subscription_labels = [data['plan__name'] for data in subscription_data]
    subscription_data = [data['count'] for data in subscription_data]
    
    # Revenue statistics
    total_revenue = UserSubscription.objects.filter(
        status='active'
    ).aggregate(
        total=Sum('plan__price')
    )['total'] or 0
    
    revenue_this_month = UserSubscription.objects.filter(
        created_at__gte=start_date
    ).aggregate(
        total=Sum('plan__price')
    )['total'] or 0
    
    revenue_growth = round((revenue_this_month / total_revenue * 100) if total_revenue > 0 else 0, 1)
    
    # Revenue data for chart
    revenue_data = UserSubscription.objects.filter(
        status='active'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('plan__price')
    ).order_by('month')
    
    revenue_labels = [data['month'].strftime('%B %Y') for data in revenue_data]
    revenue_data = [data['total'] for data in revenue_data]
    
    # Kundli statistics
    total_kundli_reports = KundliReport.objects.count()
    new_kundli_this_month = KundliReport.objects.filter(
        created_at__gte=start_date
    ).count()
    kundli_growth = round((new_kundli_this_month / total_kundli_reports * 100) if total_kundli_reports > 0 else 0, 1)
    
    # Kundli sign distribution data
    kundli_sign_data = KundliReport.objects.values(
        'birth_sign'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    kundli_sign_labels = [data['birth_sign'] for data in kundli_sign_data]
    kundli_sign_data = [data['count'] for data in kundli_sign_data]
    
    # Recent activities
    recent_activities = []
    
    # User registrations
    user_activities = CustomUser.objects.filter(
        date_joined__gte=start_date
    ).order_by('-date_joined')[:10]
    
    for user in user_activities:
        recent_activities.append({
            'type': 'user',
            'icon': 'fa-user-plus',
            'title': 'New User Registration',
            'user': user.get_full_name() or user.username,
            'user_email': user.email,
            'details': f'User registered with email {user.email}',
            'timestamp': user.date_joined,
            'status': 'success'
        })
    
    # Subscriptions
    subscription_activities = UserSubscription.objects.filter(
        created_at__gte=start_date
    ).order_by('-created_at')[:10]
    
    for sub in subscription_activities:
        recent_activities.append({
            'type': 'subscription',
            'icon': 'fa-credit-card',
            'title': 'New Subscription',
            'user': sub.user.get_full_name() or sub.user.username,
            'user_email': sub.user.email,
            'details': f'Subscribed to {sub.plan.name} plan',
            'timestamp': sub.created_at,
            'status': sub.status
        })
    
    # Kundli reports
    kundli_activities = KundliReport.objects.filter(
        created_at__gte=start_date
    ).order_by('-created_at')[:10]
    
    for kundli in kundli_activities:
        recent_activities.append({
            'type': 'kundli',
            'icon': 'fa-moon',
            'title': 'New Kundli Report',
            'user': kundli.user.get_full_name() or kundli.user.username,
            'user_email': kundli.user.email,
            'details': f'Generated Kundli report for {kundli.name}',
            'timestamp': kundli.created_at,
            'status': 'success'
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    context = {
        'total_users': total_users,
        'user_growth': user_growth,
        'user_growth_labels': json.dumps(user_growth_labels),
        'user_growth_data': json.dumps(user_growth_data),
        
        'active_subscriptions': active_subscriptions,
        'subscription_growth': subscription_growth,
        'subscription_labels': json.dumps(subscription_labels),
        'subscription_data': json.dumps(subscription_data),
        
        'total_kundli_reports': total_kundli_reports,
        'kundli_growth': kundli_growth,
        'kundli_sign_labels': json.dumps(kundli_sign_labels),
        'kundli_sign_data': json.dumps(kundli_sign_data),
        
        'total_revenue': total_revenue,
        'revenue_growth': revenue_growth,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        
        'recent_activities': recent_activities
    }
    
    return render(request, 'admin_panel/analytics/dashboard.html', context)

def chatbot(request):
    if not is_admin(request.user):
        return redirect('login')
    
    context = {
        'chatbot_status': 'online'
    }
    return render(request, 'admin_panel/chatbot/chat.html', context)

@require_http_methods(["POST"])
def send_message(request):
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Message is required'})
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare the conversation context
        conversation = [
            {"role": "system", "content": """You are an AI assistant specialized in astrology and Kundli analysis. 
            You can help with:
            1. Analyzing Kundli reports
            2. Providing horoscope predictions
            3. Explaining astrological concepts
            4. Answering questions about subscriptions and services
            5. General astrology guidance
            
            Always maintain a professional and helpful tone. If you're unsure about something, 
            acknowledge it and suggest consulting with a professional astrologer."""},
            {"role": "user", "content": message}
        ]
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def analyze_kundli_ai(request, kundli_id):
    if not is_admin(request.user):
        return redirect('login')
    
    try:
        kundli = KundliReport.objects.get(id=kundli_id)
        
        # Prepare Kundli data for AI analysis
        kundli_data = {
            'name': kundli.name,
            'birth_date': kundli.birth_date.strftime('%Y-%m-%d'),
            'birth_time': kundli.birth_time.strftime('%H:%M'),
            'birth_place': kundli.place,
            'birth_sign': kundli.birth_sign,
            'ascendant': kundli.ascendant,
            'planetary_positions': kundli.planetary_positions,
            'houses': kundli.houses,
            'yogas': kundli.yogas,
            'doshas': kundli.doshas
        }
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare the prompt for AI analysis
        prompt = f"""Analyze the following Kundli report and provide detailed insights:

Name: {kundli_data['name']}
Birth Date: {kundli_data['birth_date']}
Birth Time: {kundli_data['birth_time']}
Birth Place: {kundli_data['birth_place']}
Birth Sign: {kundli_data['birth_sign']}
Ascendant: {kundli_data['ascendant']}

Planetary Positions:
{kundli_data['planetary_positions']}

Houses:
{kundli_data['houses']}

Yogas:
{kundli_data['yogas']}

Doshas:
{kundli_data['doshas']}

Please provide a comprehensive analysis including:
1. Overall personality traits and characteristics
2. Career prospects and professional inclinations
3. Health indicators and potential concerns
4. Relationship dynamics and compatibility
5. Financial prospects and wealth indicators
6. Spiritual inclinations and growth potential
7. Major life periods and timing of significant events
8. Recommendations for personal development

Format the response in a clear, structured manner with appropriate headings and bullet points where necessary."""

        # Get AI analysis
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert astrologer with deep knowledge of Vedic astrology and Kundli analysis. Provide detailed, accurate, and insightful analysis while maintaining a professional and helpful tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        ai_analysis = response.choices[0].message.content
        
        # Save AI analysis to the Kundli report
        kundli.ai_analysis = ai_analysis
        kundli.save()
        
        context = {
            'kundli': kundli,
            'ai_analysis': ai_analysis
        }
        
        return render(request, 'admin_panel/kundli/ai_analysis.html', context)
        
    except KundliReport.DoesNotExist:
        messages.error(request, 'Kundli report not found.')
        return redirect('admin_panel:admin_kundli')
    except Exception as e:
        messages.error(request, f'Error analyzing Kundli: {str(e)}')
        return redirect('admin_panel:admin_kundli')
