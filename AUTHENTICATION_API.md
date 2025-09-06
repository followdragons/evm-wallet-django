# Authentication API for EVM Wallet

## Overview

The authentication system supports:
- **Telegram Bot** - authentication via Telegram bot
- **Telegram WebApp** - authentication via Telegram Web App
- **JWT tokens** - for API access
- **EVM addresses** - binding Ethereum and Base addresses

## Endpoints

### 1. Telegram Bot Authentication

#### `GET /api/v1/auth/telegram/login/`
Authentication via Telegram bot.

**Parameters (GET):**
- `id` - User's Telegram ID
- `first_name` - User's first name
- `last_name` - User's last name
- `username` - Telegram username
- `photo_url` - Avatar URL
- `auth_date` - Authentication date
- `hash` - Hash for verification

**Response:**
- Success: redirect to `/api/v1/wallet/` with JWT token in cookies
- Error: JSON with error description

### 2. Telegram WebApp Authentication

#### `GET /api/v1/auth/telegram/webapp/`
Authentication via Telegram Web App.

**Parameters (GET):**
- `user` - JSON with user data
- `auth_date` - Authentication date
- `hash` - Hash for verification
- `start_param` - Start parameter (for referrals)

**Response:**
```json
{
    "result": "success"
}
```

### 3. User Registration

#### `POST /api/v1/auth/register/`
User registration via API.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "telegram_id": 123456789,
    "username_tg": "username",
    "referred_by_id": 987654321
}
```

**Response:**
```json
{
    "result": "success",
    "data": {
        "created": true,
        "token": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        "referred_by_telegram_id": 987654321
    }
}
```

### 4. Authentication Check

#### `GET /api/v1/auth/check/`
Check user authentication status.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "result": "success",
    "username": "username",
    "telegram_id": 123456789
}
```

### 5. User Profile

#### `GET /api/v1/auth/profile/`
Get user profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "id": 1,
    "telegram_id": 123456789,
    "username_tg": "username",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "has_beta_access": true,
    "has_alpha_access": false,
    "is_bot_suspected": false,
    "ethereum_address": "0x...",
    "base_address": "0x...",
    "date_joined": "2025-01-05T21:00:00Z",
    "last_login": "2025-01-05T21:30:00Z"
}
```

#### `PUT /api/v1/auth/profile/`
Update user profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe"
}
```

### 6. EVM Address Management

#### `POST /api/v1/auth/address/`
Add EVM addresses to user account.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "ethereum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "base_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
}
```

**Response:**
```json
{
    "result": "success",
    "message": "Addresses added successfully"
}
```

### 7. User Cooldowns

#### `GET /api/v1/auth/cooldowns/`
Get active cooldowns for user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "result": "success",
    "data": [
        {
            "command": "claim",
            "cooldown_timestamp": "2025-01-05T21:00:00Z",
            "remaining_seconds": 3600
        }
    ]
}
```

### 8. Logout

#### `POST /api/v1/auth/logout/`
User logout.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "result": "success",
    "message": "Logged out successfully"
}
```

## Admin Endpoints

### 9. List Users

#### `GET /api/v1/auth/admin/users/`
Get list of all users (requires Admin Access).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "users": [
        {
            "id": 1,
            "telegram_id": 123456789,
            "username_tg": "username",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": true,
            "is_staff": false,
            "has_beta_access": true,
            "has_alpha_access": false,
            "is_bot_suspected": false,
            "date_joined": "2025-01-05T21:00:00Z",
            "last_login": "2025-01-05T21:30:00Z"
        }
    ]
}
```

### 10. User Details

#### `GET /api/v1/auth/admin/users/{user_id}/`
Get detailed user information (requires Admin Access).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "id": 1,
    "telegram_id": 123456789,
    "username_tg": "username",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "has_beta_access": true,
    "has_alpha_access": false,
    "is_bot_suspected": false,
    "ethereum_address": "0x...",
    "base_address": "0x...",
    "date_joined": "2025-01-05T21:00:00Z",
    "last_login": "2025-01-05T21:30:00Z"
}
```

### 11. New Users

#### `GET /api/v1/auth/admin/new-users/`
Get new users from cache (requires Admin Access).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "result": "success",
    "data": [
        {
            "id": 1,
            "telegram_id": 123456789,
            "username": "username",
            "referred_by_telegram_id": 987654321
        }
    ]
}
```

### 12. Generate JWT Tokens for Any User (No Auth Required)

#### `POST /api/v1/auth/admin/tokens/`
Generate JWT tokens for any user (no authentication - for development/testing).

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "telegram_id": 123456789
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_info": {
        "id": 1,
        "telegram_id": 123456789,
        "username_tg": "testuser",
        "is_staff": false,
        "has_alpha_access": false,
        "has_beta_access": false,
        "full_permissions_api": false
    }
}
```

**Note:** This endpoint allows generating JWT tokens for any user in the system without authentication. Useful for debugging, testing, or providing support. **WARNING:** In production, this endpoint should be commented out or protected with authentication!

## Access Levels

### 1. Full Permissions API
- Access to all API endpoints
- Can register users
- Access to admin functions

### 2. Admin Access
- Access to admin panel
- View all users
- Manage users

### 3. Beta Access
- Access to main functions
- Profile management
- Wallet operations

### 4. Alpha Access
- Access to experimental features
- Early access to new capabilities

## JWT Token

JWT tokens contain:
- `user_id` - User ID
- `telegram_id` - Telegram ID
- `exp` - Expiration time
- `iat` - Issued at time

**Lifetime:**
- Access Token: 100 years (36525 days)
- Refresh Token: 100 years (36525 days)

## Security

1. **Hash verification** - all Telegram requests are verified via HMAC-SHA256
2. **Lifetime** - auth_date should not be older than 24 hours
3. **Bot detection** - automatic bot detection
4. **JWT tokens** - secure authentication for API
5. **Access levels** - granular access permissions

## Errors

### 400 Bad Request
```json
{
    "result": "error",
    "error_message": "Missing parameters"
}
```

### 401 Unauthorized
```json
{
    "detail": "No token provided"
}
```

### 403 Forbidden
```json
{
    "detail": "User does not have access to BETA"
}
```

### 404 Not Found
```json
{
    "error": "User not found"
}
```

### 500 Internal Server Error
```json
{
    "result": "error",
    "error_message": "Internal server error"
}
```