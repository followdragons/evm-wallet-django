from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'wallet'

urlpatterns = [
    # Wallet management
    path('wallets/', views.WalletListView.as_view(), name='wallet_list'),
    path('wallets/<int:wallet_id>/', views.WalletDetailView.as_view(), name='wallet_detail'),
    path('wallets/create/', views.WalletCreateView.as_view(), name='wallet_create'),
    
    # Token balances
    path('balances/', views.TokenBalanceListView.as_view(), name='balance_list'),
    path('balances/<int:balance_id>/', views.TokenBalanceDetailView.as_view(), name='balance_detail'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Token operations
    path('tokens/', views.TokenListView.as_view(), name='token_list'),
    path('tokens/<int:token_id>/', views.TokenDetailView.as_view(), name='token_detail'),
    
    # Chain information
    path('chains/', views.EVMChainListView.as_view(), name='chain_list'),
    path('chains/<int:chain_id>/', views.EVMChainDetailView.as_view(), name='chain_detail'),
    
    # Transfer operations
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
]
