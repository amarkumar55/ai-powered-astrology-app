#!/usr/bin/env python3
"""
Example usage of the Authentication API
This script demonstrates how to interact with the authentication endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://astro.local/api/1.0/auth"

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

class AuthAPI:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.token = None
    
    def register_user(self, user_data):
        """Register a new user"""
        url = f"{self.base_url}/register/"
        
        response = self.session.post(url, json=user_data)
        
        if response.status_code == 201:
            data = response.json()
            self.token = data['token']
            print("✅ Registration successful!")
            print(f"Token: {self.token}")
            return data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.json())
            return None
    
    def login_user(self, email, password, remember_me=False):
        """Login user"""
        url = f"{self.base_url}/login/"
        
        login_data = {
            'email': email,
            'password': password,
            'remember_me': remember_me
        }
        
        response = self.session.post(url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('requires_2fa'):
                print("🔐 Two-factor authentication required")
                return self.handle_2fa(email)
            else:
                self.token = data['token']
                print("✅ Login successful!")
                print(f"Token: {self.token}")
                return data
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.json())
            return None
    
    def handle_2fa(self, email):
        """Handle two-factor authentication"""
        print("📧 OTP sent to your email. Please enter the code:")
        otp = input("Enter OTP: ")
        
        url = f"{self.base_url}/login/2fa/"
        
        twofa_data = {
            'email': email,
            'otp': otp
        }
        
        response = self.session.post(url, json=twofa_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            print("✅ 2FA successful!")
            print(f"Token: {self.token}")
            return data
        else:
            print(f"❌ 2FA failed: {response.status_code}")
            print(response.json())
            return None
    
    def logout_user(self):
        """Logout user"""
        if not self.token:
            print("❌ No token available")
            return False
        
        url = f"{self.base_url}/logout/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        response = self.session.post(url)
        
        if response.status_code == 200:
            print("✅ Logout successful!")
            self.token = None
            return True
        else:
            print(f"❌ Logout failed: {response.status_code}")
            return False
    
    def get_profile(self):
        """Get user profile"""
        if not self.token:
            print("❌ No token available")
            return None
        
        url = f"{self.base_url}/profile/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        response = self.session.get(url)
        
        if response.status_code == 200:
            print("✅ Profile retrieved successfully!")
            return response.json()
        else:
            print(f"❌ Failed to get profile: {response.status_code}")
            print(response.json())
            return None
    
    def update_profile(self, profile_data):
        """Update user profile"""
        if not self.token:
            print("❌ No token available")
            return None
        
        url = f"{self.base_url}/profile/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        response = self.session.put(url, json=profile_data)
        
        if response.status_code == 200:
            print("✅ Profile updated successfully!")
            return response.json()
        else:
            print(f"❌ Failed to update profile: {response.status_code}")
            print(response.json())
            return None
    
    def change_password(self, old_password, new_password):
        """Change password"""
        if not self.token:
            print("❌ No token available")
            return False
        
        url = f"{self.base_url}/change-password/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        password_data = {
            'old_password': old_password,
            'new_password': new_password,
            'confirm_password': new_password
        }
        
        response = self.session.post(url, json=password_data)
        
        if response.status_code == 200:
            print("✅ Password changed successfully!")
            return True
        else:
            print(f"❌ Failed to change password: {response.status_code}")
            print(response.json())
            return False
    
    def setup_2fa(self, enable=True):
        """Setup two-factor authentication"""
        if not self.token:
            print("❌ No token available")
            return False
        
        url = f"{self.base_url}/2fa-setup/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        setup_data = {
            'enable_2fa': enable
        }
        
        response = self.session.post(url, json=setup_data)
        
        if response.status_code == 200:
            status = "enabled" if enable else "disabled"
            print(f"✅ Two-factor authentication {status} successfully!")
            return True
        else:
            print(f"❌ Failed to setup 2FA: {response.status_code}")
            print(response.json())
            return False
    
    def check_auth(self):
        """Check authentication status"""
        if not self.token:
            print("❌ No token available")
            return False
        
        url = f"{self.base_url}/check-auth/"
        self.session.headers['Authorization'] = f'Token {self.token}'
        
        response = self.session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentication check successful!")
            print(f"Authenticated: {data['authenticated']}")
            return data['authenticated']
        else:
            print(f"❌ Authentication check failed: {response.status_code}")
            return False
    
    def request_password_reset(self, email):
        """Request password reset"""
        url = f"{self.base_url}/password-reset-request/"
        
        reset_data = {
            'email': email
        }
        
        response = self.session.post(url, json=reset_data)
        
        if response.status_code == 200:
            print("✅ Password reset email sent successfully!")
            return True
        else:
            print(f"❌ Failed to request password reset: {response.status_code}")
            print(response.json())
            return False


def main():
    """Example usage of the Authentication API"""
    print("🔐 Authentication API Example")
    print("=" * 50)
    
    # Initialize API client
    api = AuthAPI()
    
    # Example 1: Register a new user
    print("\n📝 Example 1: User Registration")
    print("-" * 30)
    
    user_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': f'john.doe.{datetime.now().strftime("%Y%m%d%H%M%S")}@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!',
        'birth_date': '1990-01-01',
        'gender': 'Male',
        'is_accepted_terms': True
    }
    
    registration_result = api.register_user(user_data)
    
    if registration_result:
        # Example 2: Get user profile
        print("\n👤 Example 2: Get User Profile")
        print("-" * 30)
        profile = api.get_profile()
        if profile:
            print(f"Name: {profile['first_name']} {profile['last_name']}")
            print(f"Email: {profile['email']}")
            print(f"Email Verified: {profile['is_email_verified']}")
        
        # Example 3: Update profile
        print("\n✏️ Example 3: Update Profile")
        print("-" * 30)
        update_data = {
            'first_name': 'Johnny',
            'last_name': 'Smith',
            'bio': 'Astrology enthusiast and API tester'
        }
        api.update_profile(update_data)
        
        # Example 4: Setup 2FA
        print("\n🔐 Example 4: Setup Two-Factor Authentication")
        print("-" * 30)
        api.setup_2fa(enable=True)
        
        # Example 5: Check authentication
        print("\n✅ Example 5: Check Authentication")
        print("-" * 30)
        api.check_auth()
        
        # Example 6: Logout
        print("\n🚪 Example 6: Logout")
        print("-" * 30)
        api.logout_user()
    
    # Example 7: Login with existing user
    print("\n🔑 Example 7: Login with Existing User")
    print("-" * 30)
    
    # You would need to create a user first or use existing credentials
    login_result = api.login_user('existing@example.com', 'TestPass123!')
    
    if login_result:
        # Example 8: Change password
        print("\n🔒 Example 8: Change Password")
        print("-" * 30)
        api.change_password('TestPass123!', 'NewSecurePass123!')
        
        # Logout
        api.logout_user()
    
    # Example 9: Password reset request
    print("\n📧 Example 9: Password Reset Request")
    print("-" * 30)
    api.request_password_reset('user@example.com')
    
    print("\n🎉 API Examples completed!")


if __name__ == "__main__":
    main() 