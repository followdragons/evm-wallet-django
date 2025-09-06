# EVM Wallet Django Project

## Project Description
Django project for EVM-compatible wallet with squad (team) functionality.

## Key Features
- Custom authentication via Telegram Mini App and bot
- Support for EVM-compatible blockchains (Ethereum, Base)
- Squad (team) system for group operations
- Token and balance management
- API for frontend integration

## Installation and Setup

### 1. Cloning and Environment Setup
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables Configuration
```bash
# Rename files:
# env.txt -> .env
# gitignore.txt -> .gitignore
# env.example.txt -> .env.example
# README.txt -> README.md

# Edit .env file with your settings
```

### 3. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --telegram_id YOUR_TELEGRAM_ID
```

### 4. Run Development Server
```bash
python manage.py runserver
```

## Project Structure

### Django Apps:
- **authentication** - Custom Telegram authentication
- **wallet** - Wallet and token management
- **squad** - Squad (team) system

### Main Models:
- **User** - Users with Telegram integration
- **EVMChain** - Supported blockchains
- **Token** - Tokens on various blockchains
- **Wallet** - User wallets
- **Squad** - Squads (teams)
- **SquadWallet** - Squad wallets

## API Endpoints

### Authentication
- `POST /api/v1/auth/telegram/login/` - Login via Telegram
- `POST /api/v1/auth/telegram/webapp/` - Login via Telegram Web App
- `POST /api/v1/auth/logout/` - Logout

### Wallets
- `GET /api/v1/wallet/chains/` - List supported blockchains
- `GET /api/v1/wallet/tokens/` - List tokens
- `GET /api/v1/wallet/wallets/` - User wallets
- `POST /api/v1/wallet/wallets/create/` - Create wallet

### Squads
- `GET /api/v1/squad/squads/` - List squads
- `POST /api/v1/squad/squads/create/` - Create squad
- `POST /api/v1/squad/squads/{id}/join/` - Join squad
- `POST /api/v1/squad/squads/{id}/leave/` - Leave squad

## Telegram Bot Setup

1. Create bot via @BotFather
2. Get bot token
3. Add token to .env file
4. Configure webhook for receiving updates

## EVM Blockchain Setup

1. Get API keys from RPC providers (Infura, Alchemy)
2. Add URLs to .env file
3. Configure supported tokens in Django admin

## Development

### Adding New Tokens:
1. Go to Django admin
2. Add new token in "Tokens" section
3. Specify contract address and parameters

### Creating New Squads:
1. Use API endpoint to create squad
2. Configure squad parameters (max members, publicity)
3. Manage members via API

For questions and suggestions, create issues in the repository.