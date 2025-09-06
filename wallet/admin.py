from django.contrib import admin
from django.utils.html import format_html
from .models import EVMChain, Token, Wallet, TokenBalance, Transaction, ReferralReward


@admin.register(EVMChain)
class EVMChainAdmin(admin.ModelAdmin):
    list_display = ('name', 'chain_id', 'native_currency_symbol', 'is_active', 'is_testnet', 'block_time_seconds', 'gas_price_gwei')
    list_filter = ('is_active', 'is_testnet', 'native_currency_symbol')
    search_fields = ('name', 'chain_id', 'native_currency_symbol')
    ordering = ('chain_id',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'chain_id', 'is_active', 'is_testnet')
        }),
        ('Network Settings', {
            'fields': ('rpc_url', 'explorer_url', 'block_time_seconds', 'gas_price_gwei')
        }),
        ('Native Currency', {
            'fields': ('native_currency_symbol', 'native_currency_name')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'chain', 'address_short', 'is_native', 'is_active', 'is_verified', 'decimals')
    list_filter = ('chain', 'is_native', 'is_active', 'is_verified', 'decimals')
    search_fields = ('name', 'symbol', 'address')
    ordering = ('chain', 'symbol')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('chain', 'name', 'symbol', 'address', 'decimals', 'is_native')
        }),
        ('Token Settings', {
            'fields': ('is_active', 'is_verified', 'logo_url', 'description')
        }),
        ('Trading Settings', {
            'fields': ('min_transfer_amount', 'max_transfer_amount', 'transfer_fee_percentage')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def address_short(self, obj):
        if obj.address:
            return f"{obj.address[:10]}...{obj.address[-6:]}"
        return "Native"
    address_short.short_description = 'Address'


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'chain', 'address_short', 'is_active', 'is_verified', 'created_at')
    list_filter = ('chain', 'is_active', 'is_verified', 'created_at')
    search_fields = ('user__telegram_id', 'user__username_tg', 'address')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Wallet Information', {
            'fields': ('user', 'chain', 'address', 'is_active', 'is_verified')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def address_short(self, obj):
        return f"{obj.address[:10]}...{obj.address[-6:]}"
    address_short.short_description = 'Address'


@admin.register(TokenBalance)
class TokenBalanceAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'token', 'balance', 'frozen_balance', 'available_balance', 'last_updated')
    list_filter = ('token__chain', 'token__symbol', 'last_updated')
    search_fields = ('wallet__user__telegram_id', 'wallet__user__username_tg', 'token__symbol')
    ordering = ('-last_updated',)
    
    fieldsets = (
        ('Balance Information', {
            'fields': ('wallet', 'token', 'balance', 'frozen_balance')
        }),
    )
    
    readonly_fields = ('created_at', 'last_updated')
    
    def available_balance(self, obj):
        return obj.get_available_balance()
    available_balance.short_description = 'Available Balance'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('hash_short', 'chain', 'transaction_type', 'status', 'amount', 'token', 'user', 'created_at')
    list_filter = ('chain', 'transaction_type', 'status', 'created_at')
    search_fields = ('hash', 'from_address', 'to_address', 'user__telegram_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('hash', 'chain', 'transaction_type', 'status')
        }),
        ('Transfer Details', {
            'fields': ('from_address', 'to_address', 'token', 'amount', 'user')
        }),
        ('Gas Information', {
            'fields': ('gas_used', 'gas_price', 'gas_fee')
        }),
        ('Block Information', {
            'fields': ('block_number', 'block_hash')
        }),
    )
    
    readonly_fields = ('created_at', 'confirmed_at')
    
    def hash_short(self, obj):
        return f"{obj.hash[:10]}...{obj.hash[-6:]}"
    hash_short.short_description = 'Hash'


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'token', 'amount', 'created_at')
    list_filter = ('token__chain', 'token__symbol', 'created_at')
    search_fields = ('from_user__telegram_id', 'to_user__telegram_id', 'token__symbol')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Reward Information', {
            'fields': ('from_user', 'to_user', 'token', 'amount', 'transaction')
        }),
    )
    
    readonly_fields = ('created_at',)
