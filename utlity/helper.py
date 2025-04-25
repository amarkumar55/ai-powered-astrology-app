import json
import datetime
from user_agents import parse
from django.contrib.auth import get_user_model
from authentication.models import UserActivity

def sanitize_request_data(request_data):
    sanitized_data = request_data.copy()
    if 'password' in sanitized_data:
        sanitized_data['password'] = 'xxxxxxxxxx'
    return sanitized_data


User = get_user_model() 

def store_activity(request, data, type, user):
    
    sanitized_data = sanitize_request_data(data) if data else {}
    
    for key, value in sanitized_data.items():
        if isinstance(value, (datetime.datetime, datetime.date)):
            sanitized_data[key] = value.isoformat()

    json_data = json.dumps(sanitized_data)  


    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')

    if ip_address:
        ip_address = ip_address.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    UserActivity.objects.create(
        user=user, 
        activity_type=type,
        data=json_data,
        ip_address=ip_address,
        browser=user_agent.browser.family or "Unknown",
        browser_version=user_agent.browser.version_string or "Unknown",
        os=user_agent.os.family or "Unknown",
        os_version=user_agent.os.version_string or "Unknown",
        device_brand=user_agent.device.brand or "Unknown",
        device_model=user_agent.device.model or "Unknown",
        device_type = (
                "Mobile" if user_agent.is_mobile else
                "Tablet" if user_agent.is_tablet else
                "PC" if user_agent.is_pc else
                "Other"
         )
   )
