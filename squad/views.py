from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from .models import Chat, ChatWallet, ChatTokenBalance, ChatActivity, ChatReward
from wallet.models import EVMChain, Token
import logging

logger = logging.getLogger(__name__)


class ChatListView(ListAPIView):
    """
    List all active chats
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Chat.objects.filter(is_active=True)
    
    def list(self, request):
        chats = self.get_queryset()
        chat_data = []
        for chat in chats:
            chat_data.append({
                'id': chat.id,
                'chat_id': chat.chat_id,
                'title': chat.title,
                'username': chat.username,
                'display_name': chat.get_display_name(),
                'description': chat.description,
                'is_public': chat.is_public,
                'avatar_url': chat.avatar_url,
                'created_at': chat.created_at,
            })
        return Response({'chats': chat_data}, status=status.HTTP_200_OK)


class ChatDetailView(RetrieveAPIView):
    """
    Get chat details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            return Response({
                'id': chat.id,
                'chat_id': chat.chat_id,
                'title': chat.title,
                'username': chat.username,
                'display_name': chat.get_display_name(),
                'description': chat.description,
                'is_public': chat.is_public,
                'avatar_url': chat.avatar_url,
                'created_at': chat.created_at,
                'updated_at': chat.updated_at,
            }, status=status.HTTP_200_OK)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatCreateView(CreateAPIView):
    """
    Create a new chat
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            chat_id = request.data.get('chat_id')
            title = request.data.get('title')
            username = request.data.get('username', '')
            description = request.data.get('description', '')
            
            if not chat_id or not title:
                return Response({
                    'error': 'chat_id and title are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if chat already exists
            if Chat.objects.filter(chat_id=chat_id).exists():
                return Response({
                    'error': 'Chat with this ID already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create chat
            chat = Chat.objects.create(
                chat_id=chat_id,
                title=title,
                username=username,
                description=description
            )
            
            # Create activity log
            ChatActivity.objects.create(
                chat=chat,
                user=request.user,
                activity_type='chat_created',
                description=f'Chat "{title}" was created'
            )
            
            return Response({
                'message': 'Chat created successfully',
                'chat': {
                    'id': chat.id,
                    'chat_id': chat.chat_id,
                    'title': chat.title,
                    'username': chat.username,
                    'display_name': chat.get_display_name(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating chat: {str(e)}")
            return Response({
                'error': 'Failed to create chat'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatUpdateView(UpdateAPIView):
    """
    Update chat information
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            
            # Update fields if provided
            if 'title' in request.data:
                chat.title = request.data['title']
            if 'username' in request.data:
                chat.username = request.data['username']
            if 'description' in request.data:
                chat.description = request.data['description']
            if 'is_public' in request.data:
                chat.is_public = request.data['is_public']
            if 'avatar_url' in request.data:
                chat.avatar_url = request.data['avatar_url']
            
            chat.save()
            
            # Create activity log
            ChatActivity.objects.create(
                chat=chat,
                user=request.user,
                activity_type='chat_updated',
                description=f'Chat "{chat.title}" was updated'
            )
            
            return Response({
                'message': 'Chat updated successfully',
                'chat': {
                    'id': chat.id,
                    'chat_id': chat.chat_id,
                    'title': chat.title,
                    'username': chat.username,
                    'display_name': chat.get_display_name(),
                }
            }, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating chat: {str(e)}")
            return Response({
                'error': 'Failed to update chat'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatWalletView(APIView):
    """
    Get or create chat wallet
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            
            # Get or create wallet for default chain (Ethereum)
            chain = EVMChain.objects.filter(name='Ethereum').first()
            if not chain:
                return Response({'error': 'Default chain not found'}, status=status.HTTP_404_NOT_FOUND)
            
            wallet, created = ChatWallet.objects.get_or_create(
                chat=chat,
                chain=chain,
                defaults={'is_active': True}
            )
            
            if created:
                ChatActivity.objects.create(
                    chat=chat,
                    user=request.user,
                    activity_type='wallet_created',
                    description=f'Wallet created for {chain.name}'
                )
            
            return Response({
                'wallet': {
                    'id': wallet.id,
                    'chat_id': chat.id,
                    'chat_title': chat.title,
                    'chain': chain.name,
                    'is_active': wallet.is_active,
                    'is_verified': wallet.is_verified,
                    'created_at': wallet.created_at,
                }
            }, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatBalanceListView(ListAPIView):
    """
    List chat token balances
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            wallet = ChatWallet.objects.filter(chat=chat).first()
            
            if not wallet:
                return Response({'error': 'Chat wallet not found'}, status=status.HTTP_404_NOT_FOUND)
            
            balances = ChatTokenBalance.objects.filter(chat_wallet=wallet)
            balance_data = []
            
            for balance in balances:
                balance_data.append({
                    'id': balance.id,
                    'token': {
                        'id': balance.token.id,
                        'name': balance.token.name,
                        'symbol': balance.token.symbol,
                        'address': balance.token.address,
                        'decimals': balance.token.decimals,
                        'logo_url': balance.token.logo_url,
                    },
                    'balance': str(balance.balance),
                    'frozen_balance': str(balance.frozen_balance),
                    'available_balance': str(balance.get_available_balance()),
                    'min_reward_amount': str(balance.min_reward_amount),
                    'max_reward_amount': str(balance.max_reward_amount),
                    'reward_enabled': balance.reward_enabled,
                    'last_updated': balance.last_updated,
                })
            
            return Response({'balances': balance_data}, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatBalanceDetailView(RetrieveAPIView):
    """
    Get or create chat token balance
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id, token_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            token = Token.objects.get(id=token_id)
            wallet = ChatWallet.objects.filter(chat=chat, chain=token.chain).first()
            
            if not wallet:
                return Response({'error': 'Chat wallet not found for this chain'}, status=status.HTTP_404_NOT_FOUND)
            
            balance, created = ChatTokenBalance.objects.get_or_create(
                chat_wallet=wallet,
                token=token,
                defaults={
                    'balance': 0,
                    'frozen_balance': 0,
                    'min_reward_amount': token.min_transfer_amount,
                    'max_reward_amount': token.max_transfer_amount,
                    'reward_enabled': False
                }
            )
            
            return Response({
                'balance': {
                    'id': balance.id,
                    'token': {
                        'id': balance.token.id,
                        'name': balance.token.name,
                        'symbol': balance.token.symbol,
                        'address': balance.token.address,
                        'decimals': balance.token.decimals,
                        'logo_url': balance.token.logo_url,
                    },
                    'balance': str(balance.balance),
                    'frozen_balance': str(balance.frozen_balance),
                    'available_balance': str(balance.get_available_balance()),
                    'min_reward_amount': str(balance.min_reward_amount),
                    'max_reward_amount': str(balance.max_reward_amount),
                    'reward_enabled': balance.reward_enabled,
                    'last_updated': balance.last_updated,
                    'created': created,
                }
            }, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatBalanceUpdateView(UpdateAPIView):
    """
    Update chat token balance settings
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, chat_id, balance_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            balance = ChatTokenBalance.objects.get(id=balance_id, chat_wallet__chat=chat)
            
            # Update reward settings
            if 'min_reward_amount' in request.data:
                balance.min_reward_amount = request.data['min_reward_amount']
            if 'max_reward_amount' in request.data:
                balance.max_reward_amount = request.data['max_reward_amount']
            if 'reward_enabled' in request.data:
                balance.reward_enabled = request.data['reward_enabled']
            
            balance.save()
            
            # Create activity log
            ChatActivity.objects.create(
                chat=chat,
                user=request.user,
                activity_type='balance_updated',
                description=f'Balance settings updated for {balance.token.symbol}'
            )
            
            return Response({
                'message': 'Balance settings updated successfully',
                'balance': {
                    'id': balance.id,
                    'token_symbol': balance.token.symbol,
                    'min_reward_amount': str(balance.min_reward_amount),
                    'max_reward_amount': str(balance.max_reward_amount),
                    'reward_enabled': balance.reward_enabled,
                }
            }, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        except ChatTokenBalance.DoesNotExist:
            return Response({'error': 'Balance not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatActivityListView(ListAPIView):
    """
    List chat activities
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            activities = ChatActivity.objects.filter(chat=chat).order_by('-created_at')[:50]
            
            activity_data = []
            for activity in activities:
                activity_data.append({
                    'id': activity.id,
                    'activity_type': activity.activity_type,
                    'description': activity.description,
                    'user': {
                        'id': activity.user.id,
                        'username_tg': activity.user.username_tg,
                    } if activity.user else None,
                    'metadata': activity.metadata,
                    'created_at': activity.created_at,
                })
            
            return Response({'activities': activity_data}, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatRewardListView(ListAPIView):
    """
    List chat rewards
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            rewards = ChatReward.objects.filter(chat=chat).order_by('-created_at')[:50]
            
            reward_data = []
            for reward in rewards:
                reward_data.append({
                    'id': reward.id,
                    'amount': str(reward.amount),
                    'token_symbol': reward.token_balance.token.symbol,
                    'from_user': {
                        'id': reward.from_user.id,
                        'username_tg': reward.from_user.username_tg,
                    } if reward.from_user else None,
                    'to_user': {
                        'id': reward.to_user.id,
                        'username_tg': reward.to_user.username_tg,
                    } if reward.to_user else None,
                    'message_id': reward.message_id,
                    'reason': reward.reason,
                    'created_at': reward.created_at,
                })
            
            return Response({'rewards': reward_data}, status=status.HTTP_200_OK)
            
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
