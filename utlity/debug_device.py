#!/usr/bin/env python3
"""
Debug script to test device detection functionality
"""
import sys
import os
import django

# Add the project root to Python path
sys.path.append('/home/amar-kumar/Desktop/astro')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astro.settings')
django.setup()

from user_agents import parse

def test_device_detection():
    """Test device detection with various user agent strings"""
    
    # Test user agent strings
    test_user_agents = [
        # iPhone
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        
        # Android Samsung
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        
        # iPad
        "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        
        # Desktop Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        
        # Desktop Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        
        # Empty string
        "",
        
        # None
        None
    ]
    
    print("Testing device detection...")
    print("=" * 80)
    
    for i, ua_string in enumerate(test_user_agents, 1):
        print(f"\nTest {i}:")
        print(f"User Agent: {ua_string}")
        
        if ua_string:
            try:
                user_agent = parse(ua_string)
                
                print(f"Browser: {user_agent.browser.family}")
                print(f"Browser Version: {user_agent.browser.version_string}")
                print(f"OS: {user_agent.os.family}")
                print(f"OS Version: {user_agent.os.version_string}")
                print(f"Device Brand: {user_agent.device.brand}")
                print(f"Device Model: {user_agent.device.model}")
                print(f"Is Mobile: {user_agent.is_mobile}")
                print(f"Is Tablet: {user_agent.is_tablet}")
                print(f"Is PC: {user_agent.is_pc}")
                
                # Determine device type
                device_type = (
                    "Mobile" if user_agent.is_mobile else
                    "Tablet" if user_agent.is_tablet else
                    "PC" if user_agent.is_pc else
                    "Other"
                )
                print(f"Device Type: {device_type}")
                
            except Exception as e:
                print(f"Error parsing user agent: {e}")
        else:
            print("Empty or None user agent string")
        
        print("-" * 40)

if __name__ == "__main__":
    test_device_detection() 