from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Squad(models.Model):
    """
    Squad/Team model for group activities
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    
    # Squad ownership and membership
    owner = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='owned_squads')
    members = models.ManyToManyField('authentication.User', related_name='squads', blank=True)
    
    # Squad settings
    max_members = models.PositiveIntegerField(default=50)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Squad metadata
    avatar_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Squad'
        verbose_name_plural = 'Squads'

    def __str__(self):
        return f"Squad: {self.name}"

    def get_member_count(self):
        return self.members.count() + 1  # +1 for owner

    def get_total_members(self):
        """Get total number of members including owner"""
        return self.members.count() + 1

    def add_member(self, user):
        """Add a member to the squad"""
        if self.members.count() >= self.max_members:
            raise ValidationError("Squad is at maximum capacity")
        if user in self.members.all():
            raise ValidationError("User is already a member")
        if user == self.owner:
            raise ValidationError("Owner cannot be added as a member")
        self.members.add(user)

    def remove_member(self, user):
        """Remove a member from the squad"""
        if user == self.owner:
            raise ValidationError("Cannot remove squad owner")
        self.members.remove(user)

    def is_member(self, user):
        """Check if user is a member of the squad"""
        return user == self.owner or user in self.members.all()

    def is_owner(self, user):
        """Check if user is the owner of the squad"""
        return user == self.owner




class SquadWallet(models.Model):
    """
    Shared wallet for squad funds
    """
    squad = models.OneToOneField(Squad, on_delete=models.CASCADE, related_name='wallet')
    chain = models.ForeignKey('wallet.EVMChain', on_delete=models.CASCADE, related_name='squad_wallets')
    
    # Wallet address
    address = models.CharField(max_length=42, unique=True)
    
    # Wallet settings
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Squad Wallet'
        verbose_name_plural = 'Squad Wallets'

    def __str__(self):
        return f"Squad Wallet: {self.squad.name} - {self.chain.name}"


class SquadTokenBalance(models.Model):
    """
    Token balances for squad wallets
    """
    squad_wallet = models.ForeignKey(SquadWallet, on_delete=models.CASCADE, related_name='token_balances')
    token = models.ForeignKey('wallet.Token', on_delete=models.CASCADE, related_name='squad_balances')
    
    # Balance information
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    frozen_balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    
    # Drop settings for distribution
    min_drop_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0.001'))
    max_drop_amount = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('1.0'))
    drop_enabled = models.BooleanField(default=False)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('squad_wallet', 'token')
        verbose_name = 'Squad Token Balance'
        verbose_name_plural = 'Squad Token Balances'

    def __str__(self):
        return f"{self.squad_wallet.squad.name} - {self.token.symbol}: {self.balance}"

    def get_available_balance(self):
        """Get available balance (total - frozen)"""
        return self.balance - self.frozen_balance

    def deposit(self, amount):
        """Deposit tokens to squad balance"""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw tokens from squad balance"""
        if amount <= 0:
            raise ValidationError("Withdraw amount must be positive")
        if amount > self.get_available_balance():
            raise ValidationError("Insufficient balance")
        self.balance -= amount
        self.save()

    def can_drop(self, amount):
        """Check if the amount can be dropped"""
        if not self.drop_enabled:
            return False
        if amount < self.min_drop_amount or amount > self.max_drop_amount:
            return False
        if amount > self.get_available_balance():
            return False
        return True


class SquadMemberBalance(models.Model):
    """
    Individual member balances within squad (for drops, rewards, etc.)
    """
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='squad_balances')
    token = models.ForeignKey('wallet.Token', on_delete=models.CASCADE, related_name='member_balances')
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='member_balances')
    
    # Balance information
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'token', 'squad')
        verbose_name = 'Squad Member Balance'
        verbose_name_plural = 'Squad Member Balances'

    def __str__(self):
        return f"{self.user} - {self.token.symbol} in {self.squad.name}: {self.balance}"

    def deposit(self, amount):
        """Deposit tokens to member balance"""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Withdraw tokens from member balance"""
        if amount <= 0:
            raise ValidationError("Withdraw amount must be positive")
        if amount > self.balance:
            raise ValidationError("Insufficient balance")
        self.balance -= amount
        self.save()


class SquadActivity(models.Model):
    """
    Track squad activities and events
    """
    ACTIVITY_TYPES = [
        ('member_joined', 'Member Joined'),
        ('member_left', 'Member Left'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('drop', 'Token Drop'),
        ('squad_created', 'Squad Created'),
        ('squad_updated', 'Squad Updated'),
    ]

    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='squad_activities', null=True, blank=True)
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(max_length=500)
    
    # Additional data (JSON field could be used for more complex data)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Squad Activity'
        verbose_name_plural = 'Squad Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.squad.name} - {self.activity_type} - {self.created_at}"
