from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserCooldown


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'telegram_id', 'username_tg', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('id', 'telegram_id', 'username_tg', 'first_name', 'last_name')
    ordering = ('id',)
    
    fieldsets = (
        (None, {'fields': ('id', 'telegram_id', 'password')}),
        ('Personal info', {'fields': ('username_tg', 'first_name', 'last_name')}),
        ('Wallet addresses', {'fields': ('ethereum_address', 'base_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'full_permissions_api', 'has_beta_access', 'has_alpha_access')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'username_tg', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_chain', 'email_notifications', 'telegram_notifications')
    list_filter = ('default_chain', 'email_notifications', 'telegram_notifications')
    search_fields = ('user__telegram_id', 'user__username_tg')


@admin.register(UserCooldown)
class UserCooldownAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'cooldown_until', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__telegram_id', 'user__username_tg', 'action')
