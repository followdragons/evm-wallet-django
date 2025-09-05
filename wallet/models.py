from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class EVMChain(models.Model):
    """
    EVM-compatible blockchain networks
    """
    name = models.CharField(max_length=50, unique=True)
    chain_id = models.IntegerField(unique=True)
    rpc_url = models.URLField()
    explorer_url = models.URLField(blank=True, null=True)
    native_currency_symbol = models.CharField(max_length=10, default='ETH')
    native_currency_name = models.CharField(max_length=50, default='Ethereum')
    is_active = models.BooleanField(default=True)
    is_testnet = models.BooleanField(default=False)
    
    # Chain-specific settings
    block_time_seconds = models.IntegerField(default=12)  # Average block time
    gas_price_gwei = models.DecimalField(max_digits=10, decimal_places=2, default=20.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'EVM Chain'
        verbose_name_plural = 'EVM Chains'

    def __str__(self):
        return f"{self.name} (Chain ID: {self.chain_id})"


class Token(models.Model):
    """
    ERC-20 tokens on EVM chains
    """
    chain = models.ForeignKey(EVMChain, on_delete=models.CASCADE, related_name='tokens')
    
    # Token information
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    address = models.CharField(max_length=42, blank=True, null=True)  # Contract address, null for native tokens
    decimals = models.PositiveSmallIntegerField(default=18)
    
    # Token metadata
    logo_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Token settings
    is_native = models.BooleanField(default=False)  # True for native chain currency (ETH, etc.)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Trading settings
    min_transfer_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0.001'))
    max_transfer_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('1000000'))
    transfer_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.1'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('chain', 'address')
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

    def __str__(self):
        return f"{self.symbol} on {self.chain.name}"

    def clean(self):
        if self.is_native and self.address:
            raise ValidationError("Native tokens should not have a contract address")
        if not self.is_native and not self.address:
            raise ValidationError("Non-native tokens must have a contract address")


class Wallet(models.Model):
    """
    User wallet for EVM chains
    """
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='wallets')
    chain = models.ForeignKey(EVMChain, on_delete=models.CASCADE, related_name='wallets')
    
    # Wallet address (same for all chains if using same private key)
    address = models.CharField(max_length=42, unique=True)
    
    # Wallet metadata
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chain')
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f"{self.user} - {self.chain.name} ({self.address[:10]}...)"


class TokenBalance(models.Model):
    """
    Token balances for user wallets
    """
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='token_balances')
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='balances')
    
    # Balance information
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    frozen_balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wallet', 'token')
        verbose_name = 'Token Balance'
        verbose_name_plural = 'Token Balances'

    def __str__(self):
        return f"{self.wallet.user} - {self.token.symbol}: {self.balance}"

    def get_available_balance(self):
        """Get available balance (total - frozen)"""
        return self.balance - self.frozen_balance

    def deposit(self, amount):
        """Deposit tokens to balance"""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw tokens from balance"""
        if amount <= 0:
            raise ValidationError("Withdraw amount must be positive")
        if amount > self.get_available_balance():
            raise ValidationError("Insufficient balance")
        self.balance -= amount
        self.save()

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


class Transaction(models.Model):
    """
    Blockchain transactions
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('swap', 'Swap'),
        ('stake', 'Stake'),
        ('unstake', 'Unstake'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Transaction identification
    hash = models.CharField(max_length=66, unique=True, db_index=True)  # Transaction hash
    chain = models.ForeignKey(EVMChain, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    
    # Transaction metadata
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    # Gas information
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.DecimalField(max_digits=36, decimal_places=18, null=True, blank=True)
    gas_fee = models.DecimalField(max_digits=36, decimal_places=18, null=True, blank=True)
    
    # Block information
    block_number = models.BigIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=66, blank=True, null=True)
    
    # User association
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['hash']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['chain', 'status']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.hash[:10]}... ({self.status})"


class ReferralReward(models.Model):
    """
    Referral rewards for users
    """
    from_user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='referral_rewards_given')
    to_user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='referral_rewards_received')
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='referral_rewards')
    
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='referral_rewards', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Referral Reward'
        verbose_name_plural = 'Referral Rewards'

    def __str__(self):
        return f"Referral reward: {self.amount} {self.token.symbol} from {self.from_user} to {self.to_user}"
