from datetime import datetime
from .models import Horoscope
from django.contrib import messages
from django.shortcuts import render,redirect
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from utlity.card_data  import sign_images

# @ratelimit(key='user_or_ip', rate='5/m', block=True)

# def user_horoscope(request):
#     today = datetime.now().date()  # Get today's date
#     user = request.user  # Get the current authenticated user

#     # Check if the user has a zodiac sign, if not, calculate it
#     if not user.zodiac_sign:
#         day = user.birth_date.day
#         month = user.birth_date.month
#         #user.zodiac_sign = get_zodiac_sign(day, month)  # Assuming get_zodiac_sign is a function that returns zodiac sign
#         user.save()

#     daily_horoscope = Horoscope.objects.filter(date=today, type='daily', sign=user.zodiac_sign).first()
#     weekly_horoscope = Horoscope.objects.filter(date=today, type='weekly', sign=user.zodiac_sign).first()

    
#     return render(request, 'horoscope/user_horoscope.html', {
#         'daily_horoscope': daily_horoscope,
#         'weekly_horoscope': weekly_horoscope,
#     })

  
@ratelimit(key='user_or_ip', rate='5/m', block=True)
def daily_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='daily')

        for h in horoscopes:
            sign_key = h.sign.lower()  # Use dot notation for model fields
            image_path = sign_images.get(sign_key)
            setattr(h, 'image', image_path)  # Dynamically add image attribute

    except Exception as e:
        messages.error(request, "Horoscope for today is not generated!")
        return redirect('home.index')

    return render(request, 'horoscope/daily.html', {'horoscopes': horoscopes})


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def weekly_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='weekly')
        for h in horoscopes:
            sign_key = h.sign.lower()  # Use dot notation for model fields
            image_path = sign_images.get(sign_key)
            setattr(h, 'image', image_path)  # Dynamically add image attribute
    except Exception as e:
        messages.error(request, "Horoscope for today is not generated!")
        return redirect('home.index')
    return render(request, 'horoscope/weekly.html', {'horoscopes': horoscopes})


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def monthly_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='monthly')
        for h in horoscopes:
            sign_key = h.sign.lower()  # Use dot notation for model fields
            image_path = sign_images.get(sign_key)
            setattr(h, 'image', image_path)  # Dynamically add image attribute
    except Exception as e:
        messages.error(request, "Horoscope for month is not generated!")
        return redirect('home.index')
    return render(request, 'horoscope/monthly.html', {'horoscopes': horoscopes})


@ratelimit(key='user_or_ip', rate='5/m', block=True)
def yearly_horoscope(request):
    try:
        today = datetime.now().date()
        horoscopes = Horoscope.objects.filter(date=today, type='yearly')
        for h in horoscopes:
            sign_key = h.sign.lower()  # Use dot notation for model fields
            image_path = sign_images.get(sign_key)
            setattr(h, 'image', image_path)  # Dynamically add image attribute
    except Exception as e:
        messages.error(request, "Horoscope for year is not generated!")
        return redirect('home.index')
    return render(request, 'horoscope/yearly.html', {'horoscopes': horoscopes})