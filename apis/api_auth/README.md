# Authentication API Documentation

This document provides comprehensive documentation for the secure authentication APIs built for the Astro application.

## Overview

The authentication API provides secure, robust endpoints for user registration, login, email verification, password management, and profile management. All endpoints include rate limiting, input validation, and security best practices.

## Base URL

```
https://yourdomain.com/api/auth/
```

## Authentication

Most endpoints require authentication using Token-based authentication. Include the token in the Authorization header:

```
Authorization: Token <your_token_here>
```

## Endpoints

### 1. User Registration

**POST** `/register/`

Register a new user account.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "birth_date": "1990-01-01",
    "gender": "Male",
    "is_accepted_terms": true
}
```

**Response (201 Created):**
```json
{
    "message": "Registration successful. Please check your email for verification.",
    "token": "your_auth_token_here",
    "user": {
        "id": 1,
        "email": "john.doe@example.com",
        "username": "john123456",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": false
    }
}
```

**Validation Rules:**
- Password must be at least 8 characters
- Password must contain uppercase, lowercase, digit, and special character
- User must be at least 13 years old
- Terms must be accepted
- Email must be unique and valid format

### 2. User Login

**POST** `/login/`

Authenticate user and receive access token.

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "password": "SecurePass123!",
    "remember_me": false
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful.",
    "token": "your_auth_token_here",
    "user": {
        "id": 1,
        "email": "john.doe@example.com",
        "username": "john123456",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "two_factor_enabled": false
    }
}
```

**2FA Response (200 OK):**
```json
{
    "message": "Two-factor authentication required.",
    "requires_2fa": true,
    "email": "john.doe@example.com"
}
```

### 3. Two-Factor Authentication Login

**POST** `/login/2fa/`

Complete login with 2FA OTP.

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "otp": "123456"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful.",
    "token": "your_auth_token_here",
    "user": {
        "id": 1,
        "email": "john.doe@example.com",
        "username": "john123456",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "two_factor_enabled": true
    }
}
```

### 4. User Logout

**POST** `/logout/`

**Headers:** `Authorization: Token <token>`

**Response (200 OK):**
```json
{
    "message": "Logged out successfully."
}
```

### 5. Email Verification

**POST** `/verify-email/`

Verify email address with token.

**Request Body:**
```json
{
    "uid": "base64_encoded_user_id",
    "token": "verification_token"
}
```

**Response (200 OK):**
```json
{
    "message": "Email verified successfully."
}
```

### 6. Resend Email Verification

**POST** `/resend-verification/`

**Request Body:**
```json
{
    "email": "john.doe@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "Verification email sent successfully."
}
```

### 7. Password Reset Request

**POST** `/password-reset-request/`

**Request Body:**
```json
{
    "email": "john.doe@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset email sent successfully."
}
```

### 8. Password Reset Confirmation

**POST** `/password-reset-confirm/`

**Request Body:**
```json
{
    "uid": "base64_encoded_user_id",
    "token": "reset_token",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset successfully."
}
```

### 9. Change Password

**POST** `/change-password/`

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "old_password": "CurrentPass123!",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully."
}
```

### 10. Password Verification

**POST** `/verify-password/`

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "password": "CurrentPass123!"
}
```

**Response (200 OK):**
```json
{
    "message": "Password verified successfully."
}
```

### 11. User Profile

**GET** `/profile/`

**Headers:** `Authorization: Token <token>`

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "john.doe@example.com",
    "username": "john123456",
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-01-01",
    "gender": "Male",
    "is_email_verified": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "profile_picture": null,
    "bio": null,
    "country_code": null,
    "cell": null,
    "birth_place": null,
    "latitude": null,
    "longitude": null,
    "timezone": null,
    "language_preference": "English",
    "notification_preference": true,
    "time_format": "AM",
    "zodiac_sign": null,
    "two_factor_enabled": false
}
```

### 12. Update Profile

**PUT** `/profile/`

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "bio": "Astrology enthusiast",
    "country_code": "+1",
    "cell": "1234567890",
    "birth_place": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "language_preference": "English",
    "notification_preference": true,
    "time_format": "PM"
}
```

**Response (200 OK):**
```json
{
    "message": "Profile updated successfully.",
    "user": {
        // Updated user profile data
    }
}
```

### 13. Two-Factor Authentication Setup

**POST** `/2fa-setup/`

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "enable_2fa": true
}
```

**Response (200 OK):**
```json
{
    "message": "Two-factor authentication enabled successfully.",
    "two_factor_enabled": true
}
```

### 14. Authentication Check

**GET** `/check-auth/`

**Headers:** `Authorization: Token <token>`

**Response (200 OK):**
```json
{
    "authenticated": true,
    "user": {
        // User profile data
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation error message",
    "field_name": ["Specific field error"]
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication token required."
}
```

### 403 Forbidden
```json
{
    "error": "Account is disabled."
}
```

### 429 Too Many Requests
```json
{
    "error": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error. Please try again later."
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- Registration: 5 requests per minute
- Login: 10 requests per minute
- Password reset: 3 requests per minute
- Email verification: 10 requests per minute
- Profile updates: 5 requests per minute

## Security Features

1. **Token-based Authentication**: Secure token-based authentication
2. **Password Strength**: Enforced strong password requirements
3. **Rate Limiting**: Protection against brute force attacks
4. **Input Validation**: Comprehensive input sanitization and validation
5. **Email Verification**: Required email verification for account activation
6. **Two-Factor Authentication**: Optional 2FA for enhanced security
7. **Account Status Checks**: Validation of account status (active, disabled, etc.)
8. **Secure Headers**: Security headers in all responses
9. **Request Logging**: Comprehensive request logging for monitoring

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

## Email Verification Flow

1. User registers with email
2. Verification email is sent automatically
3. User clicks verification link or uses API endpoint
4. Account is activated upon successful verification
5. User can request resend if needed

## Two-Factor Authentication Flow

1. User enables 2FA in profile settings
2. User logs in with email/password
3. System sends OTP to user's email
4. User completes login with OTP
5. User receives authentication token

## Testing

Run the comprehensive test suite:

```bash
python manage.py test api_auth.tests
```

## Middleware

The API includes several middleware components for security:

1. **APIRateLimitMiddleware**: Rate limiting for API endpoints
2. **APITokenMiddleware**: Token authentication and validation
3. **APIRequestLoggingMiddleware**: Request logging for monitoring
4. **APISecurityHeadersMiddleware**: Security headers in responses

## Integration Examples

### JavaScript/Fetch
```javascript
// Login
const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123!'
    })
});

const data = await response.json();
const token = data.token;

// Authenticated request
const profileResponse = await fetch('/api/auth/profile/', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
    }
});
```

### Python/Requests
```python
import requests

# Login
response = requests.post('https://yourdomain.com/api/auth/login/', {
    'email': 'user@example.com',
    'password': 'password123!'
})

token = response.json()['token']

# Authenticated request
headers = {'Authorization': f'Token {token}'}
profile_response = requests.get('https://yourdomain.com/api/auth/profile/', headers=headers)
```

## Best Practices

1. **Always use HTTPS** in production
2. **Store tokens securely** on the client side
3. **Implement proper error handling** for all API calls
4. **Use rate limiting** on the client side as well
5. **Validate all inputs** before sending to API
6. **Handle token expiration** gracefully
7. **Implement proper logout** to clear tokens
8. **Use secure password storage** on client side
9. **Implement proper session management**
10. **Monitor API usage** and implement alerts

## Support

For API support and questions, please contact the development team or refer to the project documentation. 