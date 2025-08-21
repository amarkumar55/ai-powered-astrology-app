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

def debug_device_detection(request):
    """
    Debug function to test device detection from a request
    Returns a dictionary with all detected information
    """
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    # Get IP address
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Extract all device information
    device_info = {
        'raw_user_agent': user_agent_string,
        'ip_address': ip_address,
        'browser_family': user_agent.browser.family,
        'browser_version': user_agent.browser.version_string,
        'os_family': user_agent.os.family,
        'os_version': user_agent.os.version_string,
        'device_brand': user_agent.device.brand,
        'device_model': user_agent.device.model,
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_pc': user_agent.is_pc,
        'is_bot': user_agent.is_bot,
        'device_type': None
    }
    
    # Determine device type
    if user_agent.is_mobile:
        device_info['device_type'] = "Mobile"
    elif user_agent.is_tablet:
        device_info['device_type'] = "Tablet"
    elif user_agent.is_pc:
        device_info['device_type'] = "PC"
    else:
        device_info['device_type'] = "Other"
    
    return device_info

def store_activity(request, data, type, user):
    
    sanitized_data = sanitize_request_data(data) if data else {}
    
    for key, value in sanitized_data.items():
        if isinstance(value, (datetime.datetime, datetime.date)):
            sanitized_data[key] = value.isoformat()

    json_data = json.dumps(sanitized_data)  

    # Get IP address
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')

    # Parse user agent
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    # Extract device information with better handling
    browser_family = user_agent.browser.family
    browser_version = user_agent.browser.version_string
    os_family = user_agent.os.family
    os_version = user_agent.os.version_string
    device_brand = user_agent.device.brand
    device_model = user_agent.device.model
    
    # Handle None values properly
    browser_family = browser_family if browser_family else "Unknown"
    browser_version = browser_version if browser_version else "Unknown"
    os_family = os_family if os_family else "Unknown"
    os_version = os_version if os_version else "Unknown"
    
    # For desktop devices, device brand and model are typically None
    # We'll set them based on the OS family for better identification
    if device_brand is None and device_model is None:
        if user_agent.is_pc:
            device_brand = os_family  # Use OS as brand for desktop
            device_model = "Desktop"  # Generic model for desktop
        else:
            device_brand = "Unknown"
            device_model = "Unknown"
    else:
        device_brand = device_brand if device_brand else "Unknown"
        device_model = device_model if device_model else "Unknown"
    
    # Determine device type
    if user_agent.is_mobile:
        device_type = "Mobile"
    elif user_agent.is_tablet:
        device_type = "Tablet"
    elif user_agent.is_pc:
        device_type = "PC"
    else:
        device_type = "Other"
    
    # Create the activity record
    UserActivity.objects.create(
        user=user, 
        activity_type=type,
        data=json_data,
        ip_address=ip_address,
        browser=browser_family,
        browser_version=browser_version,
        os=os_family,
        os_version=os_version,
        device_brand=device_brand,
        device_model=device_model,
        device_type=device_type
    )
