from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import User, UserProfile, UserCooldown
import logging

logger = logging.getLogger(__name__)


class TelegramLoginView(APIView):
    """
    Handle Telegram authentication via bot
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # TODO: Implement Telegram bot authentication
        return Response({'message': 'Telegram login endpoint'}, status=status.HTTP_200_OK)


class TelegramWebAppLoginView(APIView):
    """
    Handle Telegram Web App authentication
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # TODO: Implement Telegram Web App authentication
        return Response({'message': 'Telegram Web App login endpoint'}, status=status.HTTP_200_OK)


class TelegramLogoutView(APIView):
    """
    Handle user logout
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement logout logic
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Get and update user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'telegram_id': user.telegram_id,
            'username_tg': user.username_tg,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'ethereum_address': user.ethereum_address,
            'base_address': user.base_address,
            'has_beta_access': user.has_beta_access,
            'has_alpha_access': user.has_alpha_access,
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        # TODO: Implement profile update logic
        return Response({'message': 'Profile updated'}, status=status.HTTP_200_OK)


class UserCooldownView(APIView):
    """
    Get user cooldowns
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        cooldowns = UserCooldown.objects.filter(user=user)
        cooldown_data = []
        for cooldown in cooldowns:
            cooldown_data.append({
                'action': cooldown.action,
                'cooldown_until': cooldown.cooldown_until,
                'is_active': cooldown.cooldown_until > timezone.now()
            })
        return Response({'cooldowns': cooldown_data}, status=status.HTTP_200_OK)


class AdminUserListView(ListAPIView):
    """
    List all users (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # TODO: Add admin permission check
        return User.objects.all()
    
    def list(self, request):
        users = self.get_queryset()
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username_tg': user.username_tg,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
            })
        return Response({'users': user_data}, status=status.HTTP_200_OK)


class AdminUserDetailView(RetrieveAPIView):
    """
    Get user details (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username_tg': user.username_tg,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'has_beta_access': user.has_beta_access,
                'has_alpha_access': user.has_alpha_access,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
