from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'chat'

urlpatterns = [
    # Chat management
    path('chats/', views.ChatListView.as_view(), name='chat_list'),
    path('chats/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('chats/create/', views.ChatCreateView.as_view(), name='chat_create'),
    path('chats/<int:chat_id>/update/', views.ChatUpdateView.as_view(), name='chat_update'),
    
    # Chat wallets and balances
    path('chats/<int:chat_id>/wallet/', views.ChatWalletView.as_view(), name='chat_wallet'),
    path('chats/<int:chat_id>/balances/', views.ChatBalanceListView.as_view(), name='chat_balances'),
    path('chats/<int:chat_id>/balances/<int:token_id>/', views.ChatBalanceDetailView.as_view(), name='chat_balance_detail'),
    path('chats/<int:chat_id>/balances/<int:balance_id>/update/', views.ChatBalanceUpdateView.as_view(), name='chat_balance_update'),
    
    # Chat activities and rewards
    path('chats/<int:chat_id>/activities/', views.ChatActivityListView.as_view(), name='chat_activities'),
    path('chats/<int:chat_id>/rewards/', views.ChatRewardListView.as_view(), name='chat_rewards'),
]
