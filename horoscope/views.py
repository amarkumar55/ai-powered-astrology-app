from datetime import datetime
from .models import Horoscope
from django.contrib import messages
from django.shortcuts import render,redirect
from utlity.horoscope import get_zodiac_sign
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required


@ratelimit(key='user_or_ip', rate='5/m', block=True)
@login_required()
def user_horoscope(request):
    today = datetime.now().date()  # Get today's date
    user = request.user  # Get the current authenticated user

    # Check if the user has a zodiac sign, if not, calculate it
    if not user.zodiac_sign:
        day = user.birth_date.day
        month = user.birth_date.month
        user.zodiac_sign = get_zodiac_sign(day, month)  # Assuming get_zodiac_sign is a function that returns zodiac sign
        user.save()

  
    daily_horoscope = Horoscope.objects.filter(date=today, type='daily', sign=user.zodiac_sign).first()
    weekly_horoscope = Horoscope.objects.filter(date=today, type='weekly', sign=user.zodiac_sign).first()

    
    return render(request, 'horoscope/user_horoscope.html', {
        'daily_horoscope': daily_horoscope,
        'weekly_horoscope': weekly_horoscope,
    })

  
@ratelimit(key='user_or_ip', rate='5/m', block=True)
@login_required()
def daily_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='daily')
    except Exception as e:
        messages.error(request, "Horoscope for today is not generated!")
        return redirect('home.index')
    return render(request, 'horoscope/daily.html', {'horoscopes': horoscopes})



@ratelimit(key='user_or_ip', rate='5/m', block=True)
@login_required()
def weekly_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='weekly')
    except Exception as e:
        messages.error(request, "Horoscope for today is not generated!")
        return redirect('home.index')
    return render(request, 'horoscope/weekly.html', {'horoscopes': horoscopes})