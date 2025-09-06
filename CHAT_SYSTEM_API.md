# Chat System API Documentation

## Overview
The chat system replaces the previous squad system and provides functionality for managing Telegram chats with integrated wallets for token rewards.

## Models

### Chat
- `chat_id`: Telegram chat ID (unique)
- `title`: Chat title
- `username`: Chat username (without @)
- `is_active`: Whether the chat is active
- `is_public`: Whether the chat is public
- `description`: Chat description
- `avatar_url`: Chat avatar URL

### ChatWallet
- `chat`: One-to-one relationship with Chat
- `chain`: EVM chain (Ethereum, Base, etc.)
- `is_active`: Whether the wallet is active
- `is_verified`: Whether the wallet is verified

### ChatTokenBalance
- `chat_wallet`: Foreign key to ChatWallet
- `token`: Foreign key to Token
- `balance`: Current token balance
- `frozen_balance`: Frozen token balance
- `min_reward_amount`: Minimum reward amount for this token
- `max_reward_amount`: Maximum reward amount for this token
- `reward_enabled`: Whether rewards are enabled for this token

### ChatActivity
- `chat`: Foreign key to Chat
- `user`: User who performed the activity (optional)
- `activity_type`: Type of activity
- `description`: Activity description
- `metadata`: Additional data (JSON)

### ChatReward
- `chat`: Foreign key to Chat
- `token_balance`: Foreign key to ChatTokenBalance
- `from_user`: User who gave the reward (optional)
- `to_user`: User who received the reward (optional)
- `amount`: Reward amount
- `message_id`: Telegram message ID
- `reason`: Reason for the reward

## API Endpoints

### Chat Management

#### GET /api/v1/chat/chats/
List all active chats
- **Response**: List of chats with basic information

#### GET /api/v1/chat/chats/{chat_id}/
Get chat details
- **Response**: Detailed chat information

#### POST /api/v1/chat/chats/create/
Create a new chat
- **Body**:
  ```json
  {
    "chat_id": 123456789,
    "title": "My Chat",
    "username": "mychat",
    "description": "Chat description"
  }
  ```

#### PATCH /api/v1/chat/chats/{chat_id}/update/
Update chat information
- **Body**: Any of the chat fields to update

### Chat Wallets

#### GET /api/v1/chat/chats/{chat_id}/wallet/
Get or create chat wallet
- **Response**: Wallet information for the default chain

### Chat Balances

#### GET /api/v1/chat/chats/{chat_id}/balances/
List all token balances for the chat
- **Response**: List of token balances with reward settings

#### GET /api/v1/chat/chats/{chat_id}/balances/{token_id}/
Get or create balance for a specific token
- **Response**: Token balance information

#### PATCH /api/v1/chat/chats/{chat_id}/balances/{balance_id}/update/
Update balance settings (reward amounts, enabled status)
- **Body**:
  ```json
  {
    "min_reward_amount": "0.001",
    "max_reward_amount": "1.0",
    "reward_enabled": true
  }
  ```

### Chat Activities

#### GET /api/v1/chat/chats/{chat_id}/activities/
List chat activities
- **Response**: List of recent activities

### Chat Rewards

#### GET /api/v1/chat/chats/{chat_id}/rewards/
List chat rewards
- **Response**: List of recent rewards

## Usage Examples

### 1. Create a Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/chats/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": -1001234567890,
    "title": "My Crypto Chat",
    "username": "mycryptochat",
    "description": "A chat for crypto enthusiasts"
  }'
```

### 2. Get Chat Wallet
```bash
curl -X GET http://localhost:8000/api/v1/chat/chats/1/wallet/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Configure Token Rewards
```bash
curl -X PATCH http://localhost:8000/api/v1/chat/chats/1/balances/1/update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "min_reward_amount": "0.01",
    "max_reward_amount": "5.0",
    "reward_enabled": true
  }'
```

## Migration Notes

The system has been migrated from the squad system to the chat system:
- All squad-related models have been removed
- New chat models provide similar functionality but focused on chat management
- URLs have been updated to use `/api/v1/chat/` instead of `/api/v1/squad/`
- The app name remains `squad` to avoid migration issues, but functionality is now chat-focused

## Next Steps

1. Run migrations to apply the new models
2. Update any frontend code to use the new chat endpoints
3. Implement token deposit/withdrawal functionality
4. Add reward distribution logic
5. Integrate with Telegram bot for automatic reward distribution
