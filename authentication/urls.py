from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'authentication'

urlpatterns = [
    # Telegram authentication endpoints
    path('telegram/login/', views.TelegramLoginView.as_view(), name='telegram_login'),
    path('telegram/webapp/', views.TelegramWebAppLoginView.as_view(), name='telegram_webapp'),
    path('register/', views.RegisterUserView.as_view(), name='register_user'),
    path('check/', views.CheckAuthView.as_view(), name='check_auth'),
    path('logout/', views.TelegramLogoutView.as_view(), name='logout'),
    
    # User management
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('address/', views.EVMAddressView.as_view(), name='evm_address'),
    path('wallet/register/', views.EVMWalletRegistrationView.as_view(), name='evm_wallet_register'),
    path('networks/', views.SupportedNetworksView.as_view(), name='supported_networks'),
    path('cooldowns/', views.UserCooldownView.as_view(), name='user_cooldowns'),
    
    # Admin endpoints
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:user_id>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/new-users/', views.GetNewUsersAPIView.as_view(), name='get_new_users'),
    path('admin/tokens/', views.CustomTokenObtainPairView.as_view(), name='admin_token_obtain'),
]
