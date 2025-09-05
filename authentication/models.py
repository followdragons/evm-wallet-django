from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, telegram_id, username_tg=None, referred_by_id=None, **extra_fields):
        """
        Create and return a regular user with the given telegram_id and username_tg.
        """
        if not telegram_id:
            raise ValueError('The Telegram ID must be set')
        
        user = self.model(
            telegram_id=telegram_id,
            username_tg=username_tg,
            referred_by_id=referred_by_id,
            **extra_fields
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, username_tg=None, password=None, **extra_fields):
        """
        Create and return a superuser with the given telegram_id and username_tg.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('full_permissions_api', True)
        extra_fields.setdefault('has_beta_access', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(telegram_id, username_tg, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Telegram authentication
    """
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username_tg = models.CharField(max_length=32, blank=True, null=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    
    # Wallet address for EVM chains
    ethereum_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    base_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    
    # User permissions and access levels
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    full_permissions_api = models.BooleanField(default=False)
    has_beta_access = models.BooleanField(default=False)
    has_alpha_access = models.BooleanField(default=False)
    
    # Referral system
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # Bot detection
    is_bot_suspected = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"User {self.telegram_id} ({self.username_tg or 'No username'})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username_tg or str(self.telegram_id)

    def get_short_name(self):
        return self.first_name or self.username_tg or str(self.telegram_id)

    def get_evm_addresses(self):
        """Get all EVM addresses for this user"""
        addresses = {}
        if self.ethereum_address:
            addresses['ethereum'] = self.ethereum_address
        if self.base_address:
            addresses['base'] = self.base_address
        return addresses


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    # Wallet preferences
    default_chain = models.CharField(max_length=20, default='ethereum', choices=[
        ('ethereum', 'Ethereum'),
        ('base', 'Base'),
    ])
    
    # Notification preferences
    email_notifications = models.BooleanField(default=False)
    telegram_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user}"


class UserCooldown(models.Model):
    """
    Track user cooldowns for various actions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cooldowns')
    action = models.CharField(max_length=50, db_index=True)
    cooldown_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'action')

    def __str__(self):
        return f"{self.user} - {self.action} cooldown until {self.cooldown_until}"

    @classmethod
    def is_on_cooldown(cls, user, action):
        """Check if user is on cooldown for a specific action"""
        cooldown = cls.objects.filter(
            user=user,
            action=action,
            cooldown_until__gt=timezone.now()
        ).first()
        return cooldown is not None

    @classmethod
    def set_cooldown(cls, user, action, duration_minutes):
        """Set a cooldown for a user action"""
        cooldown_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        cooldown, created = cls.objects.get_or_create(
            user=user,
            action=action,
            defaults={'cooldown_until': cooldown_until}
        )
        if not created:
            cooldown.cooldown_until = cooldown_until
            cooldown.save()
        return cooldown
