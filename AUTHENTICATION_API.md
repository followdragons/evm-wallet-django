# API Аутентификации для EVM Wallet

## Обзор

Система аутентификации поддерживает:
- **Telegram Bot** - аутентификация через Telegram бота
- **Telegram WebApp** - аутентификация через Telegram Web App
- **JWT токены** - для API доступа
- **EVM адреса** - привязка Ethereum и Base адресов

## Endpoints

### 1. Telegram Bot Authentication

#### `GET /api/v1/auth/telegram/login/`
Аутентификация через Telegram бота.

**Параметры (GET):**
- `id` - Telegram ID пользователя
- `first_name` - Имя пользователя
- `last_name` - Фамилия пользователя
- `username` - Username в Telegram
- `photo_url` - URL аватара
- `auth_date` - Дата аутентификации
- `hash` - Хеш для проверки

**Ответ:**
- Успех: редирект на `/api/v1/wallet/` с JWT токеном в cookies
- Ошибка: JSON с описанием ошибки

### 2. Telegram WebApp Authentication

#### `GET /api/v1/auth/telegram/webapp/`
Аутентификация через Telegram Web App.

**Параметры (GET):**
- `user` - JSON с данными пользователя
- `auth_date` - Дата аутентификации
- `hash` - Хеш для проверки
- `start_param` - Параметр запуска (для рефералов)

**Ответ:**
```json
{
    "result": "success"
}
```

### 3. User Registration

#### `POST /api/v1/auth/register/`
Регистрация пользователя (требует Full Permissions API).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Тело запроса:**
```json
{
    "telegram_id": 123456789,
    "username_tg": "username",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "referred_by_id": 987654321
}
```

**Ответ:**
```json
{
    "result": "success",
    "data": {
        "created": true,
        "token": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        "beta": false,
        "alpha": false,
        "referred_by_telegram_id": 987654321
    }
}
```

### 4. Check Authentication

#### `GET /api/v1/auth/check/`
Проверка аутентификации (требует Beta Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
```json
{
    "result": "success",
    "username": "username",
    "telegram_id": 123456789
}
```

### 5. User Profile

#### `GET /api/v1/auth/profile/`
Получение профиля пользователя (требует Beta Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
```json
{
    "telegram_id": 123456789,
    "username_tg": "username",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "ethereum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "base_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "has_beta_access": true,
    "has_alpha_access": false,
    "is_bot_suspected": false,
    "date_joined": "2025-01-05T21:00:00Z",
    "last_login": "2025-01-05T21:30:00Z"
}
```

### 6. EVM Address Management

#### `POST /api/v1/auth/address/`
Добавление EVM адреса к пользователю (требует Beta Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Тело запроса:**
```json
{
    "chain": "ethereum",
    "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
}
```

**Ответ:**
```json
{
    "result": "success",
    "message": "Ethereum address added successfully"
}
```

### 7. User Cooldowns

#### `GET /api/v1/auth/cooldowns/`
Получение кулдаунов пользователя (требует Beta Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
```json
{
    "cooldowns": [
        {
            "action": "transfer",
            "cooldown_until": "2025-01-05T22:00:00Z",
            "is_active": true
        }
    ]
}
```

### 8. Logout

#### `POST /api/v1/auth/logout/`
Выход из системы (требует Beta Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
- Редирект на `/api/v1/auth/`

## Admin Endpoints

### 9. List Users

#### `GET /api/v1/auth/admin/users/`
Получение списка всех пользователей (требует Admin Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
```json
{
    "users": [
        {
            "id": 1,
            "telegram_id": 123456789,
            "username_tg": "username",
            "first_name": "Имя",
            "last_name": "Фамилия",
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
Получение детальной информации о пользователе (требует Admin Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
```json
{
    "id": 1,
    "telegram_id": 123456789,
    "username_tg": "username",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "ethereum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "base_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "is_active": true,
    "is_staff": false,
    "has_beta_access": true,
    "has_alpha_access": false,
    "is_bot_suspected": false,
    "date_joined": "2025-01-05T21:00:00Z",
    "last_login": "2025-01-05T21:30:00Z"
}
```

### 11. New Users

#### `GET /api/v1/auth/admin/new-users/`
Получение новых пользователей из кэша (требует Admin Access).

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Ответ:**
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
Генерация JWT токенов для любого пользователя (без аутентификации - для разработки/тестирования).

**Заголовки:**
```
Content-Type: application/json
```

**Тело запроса:**
```json
{
    "telegram_id": 123456789
}
```

**Ответ:**
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

**Примечание:** Этот endpoint позволяет генерировать JWT токены для любого пользователя в системе без аутентификации. Полезно для отладки, тестирования или предоставления поддержки. **ВНИМАНИЕ:** В продакшене этот endpoint должен быть закомментирован или защищен аутентификацией!

## Уровни доступа

### 1. Full Permissions API
- Доступ ко всем API endpoints
- Может регистрировать пользователей
- Доступ к админ функциям

### 2. Admin Access
- Доступ к админ панели
- Просмотр всех пользователей
- Управление пользователями

### 3. Beta Access
- Доступ к основным функциям
- Управление профилем
- Работа с кошельками

### 4. Alpha Access
- Доступ к экспериментальным функциям
- Ранний доступ к новым возможностям

## JWT Token

JWT токены содержат:
- `user_id` - ID пользователя
- `telegram_id` - Telegram ID
- `exp` - Время истечения
- `iat` - Время создания

**Время жизни:**
 нужн- Access Token: 100 лет (36525 дней)
- Refresh Token: 100 лет (36525 дней)

## Безопасность

1. **Хеш проверка** - все Telegram запросы проверяются через HMAC-SHA256
2. **Время жизни** - auth_date не должен быть старше 24 часов
3. **Bot detection** - автоматическое обнаружение ботов
4. **JWT токены** - безопасная аутентификация для API
5. **Уровни доступа** - гранулярные права доступа

## Ошибки

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
