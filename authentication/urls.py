from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'authentication'

urlpatterns = [
    # Telegram authentication endpoints
    path('telegram/login/', views.TelegramLoginView.as_view(), name='telegram_login'),
    path('telegram/webapp/', views.TelegramWebAppLoginView.as_view(), name='telegram_webapp'),
    path('telegram/logout/', views.TelegramLogoutView.as_view(), name='telegram_logout'),
    
    # User management
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/cooldowns/', views.UserCooldownView.as_view(), name='user_cooldowns'),
    
    # Admin endpoints
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:user_id>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
]
