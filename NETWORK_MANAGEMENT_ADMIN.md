# Network Management in Django Admin

## Overview
Система управления блокчейн сетями через Django Admin интерфейс. Позволяет администраторам настраивать поддерживаемые EVM-совместимые сети, токены и управлять кошельками пользователей.

## Доступные модели в админке

### 1. EVM Chains (Сети)
**Путь в админке**: `/admin/wallet/evmchain/`

#### Поля для настройки:
- **Basic Information**:
  - `name` - Название сети (например, "Ethereum", "Base")
  - `chain_id` - Уникальный ID сети
  - `is_active` - Активна ли сеть
  - `is_testnet` - Тестовая сеть или основная

- **Network Settings**:
  - `rpc_url` - URL RPC узла
  - `explorer_url` - URL блокчейн эксплорера
  - `block_time_seconds` - Среднее время блока в секундах
  - `gas_price_gwei` - Рекомендуемая цена газа в Gwei

- **Native Currency**:
  - `native_currency_symbol` - Символ нативной валюты (ETH, BNB, etc.)
  - `native_currency_name` - Полное название валюты

#### Примеры настроек:

**Ethereum Mainnet**:
```
Name: Ethereum
Chain ID: 1
RPC URL: https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
Explorer URL: https://etherscan.io
Native Currency Symbol: ETH
Native Currency Name: Ethereum
Is Active: ✓
Is Testnet: ✗
Block Time Seconds: 12
Gas Price Gwei: 20.0
```

**Base Mainnet**:
```
Name: Base
Chain ID: 8453
RPC URL: https://mainnet.base.org
Explorer URL: https://basescan.org
Native Currency Symbol: ETH
Native Currency Name: Ethereum
Is Active: ✓
Is Testnet: ✗
Block Time Seconds: 2
Gas Price Gwei: 0.001
```

### 2. Tokens (Токены)
**Путь в админке**: `/admin/wallet/token/`

#### Поля для настройки:
- **Basic Information**:
  - `chain` - Сеть, к которой привязан токен
  - `name` - Полное название токена
  - `symbol` - Символ токена (USDT, USDC, etc.)
  - `address` - Адрес контракта (пустой для нативных токенов)
  - `decimals` - Количество десятичных знаков
  - `is_native` - Нативный токен сети

- **Token Settings**:
  - `is_active` - Активен ли токен
  - `is_verified` - Проверен ли токен
  - `logo_url` - URL логотипа токена
  - `description` - Описание токена

- **Trading Settings**:
  - `min_transfer_amount` - Минимальная сумма перевода
  - `max_transfer_amount` - Максимальная сумма перевода
  - `transfer_fee_percentage` - Процент комиссии за перевод

#### Примеры настроек:

**USDT на Ethereum**:
```
Chain: Ethereum
Name: Tether USD
Symbol: USDT
Address: 0xdAC17F958D2ee523a2206206994597C13D831ec7
Decimals: 6
Is Native: ✗
Is Active: ✓
Is Verified: ✓
Min Transfer Amount: 1.0
Max Transfer Amount: 1000000.0
Transfer Fee Percentage: 0.1
```

**ETH на Ethereum**:
```
Chain: Ethereum
Name: Ethereum
Symbol: ETH
Address: (пустое)
Decimals: 18
Is Native: ✓
Is Active: ✓
Is Verified: ✓
Min Transfer Amount: 0.001
Max Transfer Amount: 1000.0
Transfer Fee Percentage: 0.0
```

### 3. Wallets (Кошельки)
**Путь в админке**: `/admin/wallet/wallet/`

Показывает все зарегистрированные кошельки пользователей с возможностью:
- Просмотра адресов кошельков
- Активации/деактивации кошельков
- Верификации кошельков
- Поиска по пользователю или адресу

### 4. Token Balances (Балансы токенов)
**Путь в админке**: `/admin/wallet/tokenbalance/`

Показывает балансы пользователей по токенам:
- Общий баланс
- Замороженный баланс
- Доступный баланс (общий - замороженный)
- Последнее обновление

### 5. Transactions (Транзакции)
**Путь в админке**: `/admin/wallet/transaction/`

Показывает все транзакции в системе:
- Хеш транзакции
- Тип транзакции (deposit, withdrawal, transfer, etc.)
- Статус (pending, confirmed, failed)
- Сумма и токен
- Информация о газе
- Блокчейн информация

### 6. Referral Rewards (Реферальные награды)
**Путь в админке**: `/admin/wallet/referralreward/`

Показывает реферальные награды между пользователями.

## API Integration

### Обновленный API для регистрации кошельков
API эндпоинт `/api/v1/auth/wallet/register/` теперь использует настройки сетей из базы данных:

- Проверяет активность сети
- Возвращает информацию о сети в ответе
- Поддерживает любые сети, добавленные через админку

### Новый API для получения списка сетей
**Endpoint**: `GET /api/v1/auth/networks/`

Возвращает список всех активных сетей:

```json
{
    "result": "success",
    "data": {
        "networks": [
            {
                "name": "Ethereum",
                "chain_id": 1,
                "native_currency_symbol": "ETH",
                "native_currency_name": "Ethereum",
                "is_testnet": false,
                "block_time_seconds": 12,
                "gas_price_gwei": 20.0,
                "explorer_url": "https://etherscan.io"
            },
            {
                "name": "Base",
                "chain_id": 8453,
                "native_currency_symbol": "ETH",
                "native_currency_name": "Ethereum",
                "is_testnet": false,
                "block_time_seconds": 2,
                "gas_price_gwei": 0.001,
                "explorer_url": "https://basescan.org"
            }
        ],
        "total_count": 2
    }
}
```

## Как добавить новую сеть

1. Зайдите в Django Admin (`/admin/`)
2. Перейдите в раздел "Wallet" → "EVM Chains"
3. Нажмите "Add EVM Chain"
4. Заполните все необходимые поля:
   - Название сети
   - Chain ID
   - RPC URL
   - URL эксплорера
   - Настройки нативной валюты
   - Параметры сети (время блока, цена газа)
5. Сохраните

После добавления сети она автоматически станет доступной в API для регистрации кошельков.

## Как добавить новый токен

1. Перейдите в "Wallet" → "Tokens"
2. Нажмите "Add Token"
3. Выберите сеть
4. Заполните информацию о токене:
   - Название и символ
   - Адрес контракта (если не нативный)
   - Количество десятичных знаков
   - Настройки торговли
5. Сохраните

## Безопасность

- Все изменения в админке логируются
- Только пользователи с правами администратора могут изменять настройки
- API проверяет активность сетей перед использованием
- Валидация всех входных данных

## Мониторинг

В админке доступны:
- Список всех кошельков пользователей
- Балансы по токенам
- История транзакций
- Реферальные награды
- Статистика по сетям и токенам
