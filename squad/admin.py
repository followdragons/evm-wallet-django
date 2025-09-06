from django.contrib import admin
from .models import Chat, ChatWallet, ChatTokenBalance, ChatActivity, ChatReward


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'title', 'username', 'is_active', 'is_public', 'created_at']
    list_filter = ['is_active', 'is_public', 'created_at']
    search_fields = ['title', 'username', 'chat_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ChatWallet)
class ChatWalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'chain', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'chain', 'created_at']
    search_fields = ['chat__title', 'chat__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ChatTokenBalance)
class ChatTokenBalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_wallet', 'token', 'balance', 'reward_enabled', 'min_reward_amount', 'max_reward_amount']
    list_filter = ['reward_enabled', 'token__chain', 'created_at']
    search_fields = ['chat_wallet__chat__title', 'token__symbol', 'token__name']
    readonly_fields = ['balance', 'frozen_balance', 'last_updated', 'created_at']
    ordering = ['-last_updated']


@admin.register(ChatActivity)
class ChatActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'activity_type', 'user', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['chat__title', 'description', 'user__username_tg']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ChatReward)
class ChatRewardAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'token_balance', 'amount', 'from_user', 'to_user', 'created_at']
    list_filter = ['created_at', 'token_balance__token__symbol']
    search_fields = ['chat__title', 'from_user__username_tg', 'to_user__username_tg', 'reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
