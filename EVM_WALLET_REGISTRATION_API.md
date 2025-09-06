# EVM Wallet Registration API

## Overview
API эндпоинт для регистрации и обновления EVM кошельков пользователями. Пользователи могут зарегистрировать или обновить свои адреса кошельков для Ethereum и Base сетей.

## Endpoint
```
POST /api/v1/auth/wallet/register/
GET /api/v1/auth/wallet/register/
```

## Authentication
Требуется JWT токен в заголовке `Authorization: Bearer <token>` или в cookie `jwt_token`.

## POST - Register/Update Wallet Address

### Request
```json
{
    "chain": "ethereum" | "base",
    "address": "0x..."
}
```

### Parameters
- `chain` (string, required): Поддерживаемые сети - "ethereum" или "base"
- `address` (string, required): EVM адрес кошелька в формате 0x...

### Response

#### Success (200 OK)
```json
{
    "result": "success",
    "message": "Ethereum wallet address registered successfully",
    "data": {
        "chain": "ethereum",
        "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "old_address": null,
        "user_id": 123,
        "telegram_id": 987654321
    }
}
```

#### Error Responses

**400 Bad Request - Missing fields**
```json
{
    "result": "error",
    "error_message": "Chain and address are required"
}
```

**400 Bad Request - Invalid chain**
```json
{
    "result": "error",
    "error_message": "Invalid chain. Supported chains: ethereum, base"
}
```

**400 Bad Request - Invalid address format**
```json
{
    "result": "error",
    "error_message": "Invalid EVM address format"
}
```

**400 Bad Request - Address already registered**
```json
{
    "result": "error",
    "error_message": "This address is already registered to another user"
}
```

**401 Unauthorized**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**500 Internal Server Error**
```json
{
    "result": "error",
    "error_message": "Internal server error"
}
```

## GET - Get Current Wallet Addresses

### Request
GET запрос без параметров.

### Response

#### Success (200 OK)
```json
{
    "result": "success",
    "data": {
        "user_id": 123,
        "telegram_id": 987654321,
        "ethereum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "base_address": "0x8ba1f109551bD432803012645Hac136c4c8b4d8b6",
        "has_ethereum": true,
        "has_base": true
    }
}
```

## Features

### Address Validation
- Проверка формата EVM адреса (0x + 40 hex символов)
- Проверка уникальности адреса (не может принадлежать другому пользователю)

### Chain Support
- **Ethereum**: Основная сеть Ethereum
- **Base**: Base Layer 2 сеть

### Update Logic
- Если у пользователя уже есть адрес для указанной сети, он будет заменен на новый
- Старый адрес возвращается в поле `old_address` в ответе

## Usage Examples

### Register Ethereum Wallet
```bash
curl -X POST "https://your-domain.com/api/v1/auth/wallet/register/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum",
    "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
  }'
```

### Register Base Wallet
```bash
curl -X POST "https://your-domain.com/api/v1/auth/wallet/register/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "base",
    "address": "0x8ba1f109551bD432803012645Hac136c4c8b4d8b6"
  }'
```

### Get Current Wallets
```bash
curl -X GET "https://your-domain.com/api/v1/auth/wallet/register/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Notes
- Все запросы требуют валидный JWT токен
- Адреса проверяются на уникальность в системе
- Валидация формата адреса предотвращает некорректные данные
- Логирование всех операций регистрации/обновления кошельков

## Database Schema
Адреса кошельков сохраняются в полях модели User:
- `ethereum_address`: CharField(max_length=42, unique=True)
- `base_address`: CharField(max_length=42, unique=True)
