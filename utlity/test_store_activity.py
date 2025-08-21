#!/usr/bin/env python3
"""
Test script to verify the improved store_activity function
"""
import sys
import os
import django
from unittest.mock import Mock

# Add the project root to Python path
sys.path.append('/home/amar-kumar/Desktop/astro')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astro.settings')
django.setup()

from utlity.helper import debug_device_detection

def test_store_activity_logic():
    """Test the device detection logic without creating actual database records"""
    
    # Test user agent strings
    test_cases = [
        {
            'name': 'iPhone',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'expected_device_type': 'Mobile',
            'expected_brand': 'Apple',
            'expected_model': 'iPhone'
        },
        {
            'name': 'Android Samsung',
            'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'expected_device_type': 'Mobile',
            'expected_brand': 'Samsung',
            'expected_model': 'SM-G991B'
        },
        {
            'name': 'iPad',
            'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'expected_device_type': 'Tablet',
            'expected_brand': 'Apple',
            'expected_model': 'iPad'
        },
        {
            'name': 'Desktop Chrome',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'expected_device_type': 'PC',
            'expected_brand': 'Windows',  # Should use OS as brand
            'expected_model': 'Desktop'   # Should use generic desktop model
        },
        {
            'name': 'Desktop Firefox',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'expected_device_type': 'PC',
            'expected_brand': 'Windows',  # Should use OS as brand
            'expected_model': 'Desktop'   # Should use generic desktop model
        }
    ]
    
    print("Testing improved store_activity logic...")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"User Agent: {test_case['user_agent']}")
        
        # Create a mock request
        mock_request = Mock()
        mock_request.META = {
            'HTTP_USER_AGENT': test_case['user_agent'],
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # Get device info using our debug function
        device_info = debug_device_detection(mock_request)
        
        print(f"Detected Device Type: {device_info['device_type']}")
        print(f"Detected Brand: {device_info['device_brand']}")
        print(f"Detected Model: {device_info['device_model']}")
        print(f"Browser: {device_info['browser_family']}")
        print(f"OS: {device_info['os_family']}")
        
        # Check if our improved logic would work correctly
        if device_info['device_brand'] is None and device_info['device_model'] is None:
            if device_info['is_pc']:
                improved_brand = device_info['os_family']
                improved_model = "Desktop"
            else:
                improved_brand = "Unknown"
                improved_model = "Unknown"
        else:
            improved_brand = device_info['device_brand'] or "Unknown"
            improved_model = device_info['device_model'] or "Unknown"
        
        print(f"Improved Brand: {improved_brand}")
        print(f"Improved Model: {improved_model}")
        
        # Verify expectations
        if device_info['device_type'] == test_case['expected_device_type']:
            print("✓ Device type detection: PASSED")
        else:
            print(f"✗ Device type detection: FAILED (expected {test_case['expected_device_type']}, got {device_info['device_type']})")
        
        print("-" * 40)

if __name__ == "__main__":
    test_store_activity_logic() 