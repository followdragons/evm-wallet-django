from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Chat(models.Model):
    """
    Chat model for managing Telegram chats
    """
    # Chat identification
    chat_id = models.BigIntegerField(unique=True, db_index=True)  # Telegram chat ID
    title = models.CharField(max_length=255)  # Chat title
    username = models.CharField(max_length=255, blank=True, null=True)  # Chat username (without @)
    
    # Chat settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Chat metadata
    description = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'

    def __str__(self):
        return f"Chat: {self.title} (@{self.username or 'no_username'})"

    def get_display_name(self):
        """Get display name for the chat"""
        if self.username:
            return f"@{self.username}"
        return self.title


class ChatWallet(models.Model):
    """
    Wallet for each chat to hold supported tokens
    """
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name='wallet')
    chain = models.ForeignKey('wallet.EVMChain', on_delete=models.CASCADE, related_name='chat_wallets')
    
    # Wallet settings
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chat Wallet'
        verbose_name_plural = 'Chat Wallets'

    def __str__(self):
        return f"Chat Wallet: {self.chat.title} - {self.chain.name}"


class ChatTokenBalance(models.Model):
    """
    Token balances for chat wallets with reward settings
    """
    chat_wallet = models.ForeignKey(ChatWallet, on_delete=models.CASCADE, related_name='token_balances')
    token = models.ForeignKey('wallet.Token', on_delete=models.CASCADE, related_name='chat_balances')
    
    # Balance information
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    frozen_balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    
    # Reward settings for this token in this chat
    min_reward_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0.001'))
    max_reward_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('1.0'))
    reward_enabled = models.BooleanField(default=False)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat_wallet', 'token')
        verbose_name = 'Chat Token Balance'
        verbose_name_plural = 'Chat Token Balances'

    def __str__(self):
        return f"{self.chat_wallet.chat.title} - {self.token.symbol}: {self.balance}"

    def get_available_balance(self):
        """Get available balance (total - frozen)"""
        return self.balance - self.frozen_balance

    def deposit(self, amount):
        """Deposit tokens to chat balance"""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw tokens from chat balance"""
        if amount <= 0:
            raise ValidationError("Withdraw amount must be positive")
        if amount > self.get_available_balance():
            raise ValidationError("Insufficient balance")
        self.balance -= amount
        self.save()

    def can_reward(self, amount):
        """Check if the amount can be used for rewards"""
        if not self.reward_enabled:
            return False
        if amount < self.min_reward_amount or amount > self.max_reward_amount:
            return False
        if amount > self.get_available_balance():
            return False
        return True

    def freeze(self, amount):
        """Freeze tokens (make them unavailable for withdrawal)"""
        if amount <= 0:
            raise ValidationError("Freeze amount must be positive")
        if amount > self.get_available_balance():
            raise ValidationError("Insufficient available balance")
        self.frozen_balance += amount
        self.save()

    def unfreeze(self, amount):
        """Unfreeze tokens"""
        if amount <= 0:
            raise ValidationError("Unfreeze amount must be positive")
        if amount > self.frozen_balance:
            raise ValidationError("Insufficient frozen balance")
        self.frozen_balance -= amount
        self.save()


class ChatActivity(models.Model):
    """
    Track chat activities and events
    """
    ACTIVITY_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('reward', 'Token Reward'),
        ('chat_created', 'Chat Created'),
        ('chat_updated', 'Chat Updated'),
        ('wallet_created', 'Wallet Created'),
        ('balance_updated', 'Balance Updated'),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='chat_activities', null=True, blank=True)
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(max_length=500)
    
    # Additional data (JSON field for more complex data)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Activity'
        verbose_name_plural = 'Chat Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.chat.title} - {self.activity_type} - {self.created_at}"


class ChatReward(models.Model):
    """
    Track token rewards given in chats
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='rewards')
    token_balance = models.ForeignKey(ChatTokenBalance, on_delete=models.CASCADE, related_name='rewards')
    from_user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='rewards_given', null=True, blank=True)
    to_user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='rewards_received', null=True, blank=True)
    
    # Reward details
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    message_id = models.BigIntegerField(null=True, blank=True)  # Telegram message ID
    reason = models.CharField(max_length=255, blank=True)  # Reason for reward
    
    # Transaction reference
    transaction = models.ForeignKey('wallet.Transaction', on_delete=models.CASCADE, related_name='chat_rewards', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Reward'
        verbose_name_plural = 'Chat Rewards'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reward: {self.amount} {self.token_balance.token.symbol} in {self.chat.title}"
