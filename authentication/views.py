import hashlib
import hmac
import json
import logging
import time
import traceback
import re
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from decouple import config

from .models import User, UserProfile, UserCooldown
from wallet.models import EVMChain

logger = logging.getLogger(__name__)


# Utility Functions
def validate_evm_address(address):
    """
    Validate EVM address format (Ethereum, Base, etc.)
    """
    if not address:
        return False
    
    # Check if address starts with 0x and is 42 characters long
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    
    return True


# Custom JWT Authentication Classes
class FullPermissionsJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication class to authenticate requests based on authorized FULL PERMISSIONS API requests.
    """

    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Call the parent class's authenticate method to perform basic JWT authentication
        auth_result = super().authenticate(request)
        if auth_result == None:
            raise AuthenticationFailed('No token provided')

        user, _ = auth_result

        if auth_result is None or not isinstance(auth_result, tuple):
            raise AuthenticationFailed('No valid user found for given credentials.')

        # Check if the user has full API permissions
        if not user.full_permissions_api:
            raise AuthenticationFailed('User does not have full API permissions')

        return auth_result


class AdminJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication class to authenticate requests based on authorized ADMIN requests.
    """

    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Check if JWT token is in the headers
        header = self.get_header(request)
        raw_token = None
        if header is not None:
            raw_token = self.get_raw_token(header)

        # If no token in the headers, check the cookies
        if raw_token is None:
            raw_token = request.COOKIES.get('jwt_token')

        if raw_token is None:
            raise AuthenticationFailed('No token provided')

        validated_token = self.get_validated_token(raw_token)

        user = self.get_user(validated_token)
        if user is None or not isinstance(user, User):
            raise AuthenticationFailed('No valid user found for given credentials.')

        # Check if the user is staff
        if not user.is_staff:
            raise AuthenticationFailed('User does not have permissions to send this request')

        return user, validated_token


class BetaAccessJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication class to authenticate requests based on authorized BETA ACCESS requests.
    """

    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Check if JWT token is in the headers
        header = self.get_header(request)
        raw_token = None
        if header is not None:
            raw_token = self.get_raw_token(header)

        # If no token in the headers, check the cookies
        if raw_token is None:
            raw_token = request.COOKIES.get('jwt_token')

        if raw_token is None:
            raise AuthenticationFailed('No token provided')

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        if user is None or not isinstance(user, User):
            raise AuthenticationFailed('No valid user found for given credentials.')

        # Check if the user has beta access
        if not user.has_beta_access:
            raise AuthenticationFailed('User does not have access to BETA')

        # Update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user, validated_token


class AlphaAccessJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication class to authenticate requests based on authorized ALPHA ACCESS requests.
    """

    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Check if JWT token is in the headers
        header = self.get_header(request)
        raw_token = None
        if header is not None:
            raw_token = self.get_raw_token(header)

        # If no token in the headers, check the cookies
        if raw_token is None:
            raw_token = request.COOKIES.get('jwt_token')

        if raw_token is None:
            raise AuthenticationFailed('No token provided')

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        if user is None or not isinstance(user, User):
            raise AuthenticationFailed('No valid user found for given credentials.')

        if not user.has_alpha_access:
            raise AuthenticationFailed('User does not have access to ALPHA')

        # Update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user, validated_token


# Bot Detection Function
def detect_bot(telegram_id, referred_by_id):
    """
    Detect if the user is a bot based on the absence of a username and referral patterns.
    """
    # Check if the new user lacks a username
    user_without_username = User.objects.filter(telegram_id=int(telegram_id), username_tg__isnull=True).exists()

    if user_without_username:
        # Count how many users referred by the same user lack usernames
        if referred_by_id:
            referred_by_user = User.objects.get(id=int(referred_by_id))
            users_without_usernames_count = User.objects.filter(referred_by=referred_by_user,
                                                                username_tg__isnull=True).count()
            if users_without_usernames_count > 15:  # Threshold for flagging as bot
                return True

    return False


# User Registration Function
def register_user_func_params(user_telegram_id: int, user_username_tg: str, user_first_name: str = None, 
                            user_last_name: str = None, referred_by_id: int = None):
    try:
        with transaction.atomic():
            user, created, referred_by_telegram_id = User.objects.create_user(
                telegram_id=user_telegram_id,
                username_tg=user_username_tg,
                first_name=user_first_name,
                last_name=user_last_name,
                referred_by_id=referred_by_id,
            )

            if not created:
                logger.info(f"register_user_func - User already exists. Telegram ID: {user_telegram_id}")
                return user, created, None
            else:
                # Bot detection logic
                if detect_bot(user_telegram_id, referred_by_id):
                    user.is_bot_suspected = True
                    user.save()
                    referred_by_telegram_id = None

                logger.info(f"register_user_func - User registered successfully. Telegram ID: {user_telegram_id}")
                return user, created, referred_by_telegram_id
    except Exception as e:
        logger.error(f"register_user_func - An error occurred during user registration: {traceback.format_exc()}")
        raise ValueError(f"{e}")


# Telegram Web App Authentication
class TelegramWebAppLoginView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            data = request.GET
            user_data = data.get('user')
            auth_date = data.get('auth_date')
            received_hash = data.get('hash')
            start_param = data.get('start_param')

            if not user_data or not auth_date or not received_hash:
                return JsonResponse({'result': 'error', 'error_message': 'Missing parameters'}, status=400)

            # Create data check string
            data_check_string = "\n".join([f"{key}={value}" for key, value in sorted(data.items()) if key != 'hash'])

            # Compute the secret key using the bot token and the constant string "WebAppData"
            secret_key = hmac.new(
                key="WebAppData".encode('utf-8'),
                msg=config('TELEGRAM_BOT_TOKEN').encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            # Compute the hash of the data check string using the secret key
            computed_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

            # Compare the computed hash with the received hash
            if not hmac.compare_digest(computed_hash, received_hash):
                logger.error("TelegramWebAppAuthView - Hash mismatch")
                return JsonResponse({'result': 'error', 'error_message': 'Invalid authentication data'}, status=400)

            # Check if auth_date is within 24 hours
            if time.time() - int(auth_date) > 86400:
                logger.error("TelegramWebAppAuthView - Authentication date expired")
                return JsonResponse({'result': 'error', 'error_message': 'Authentication date expired'}, status=400)

            # Decode user data from JSON
            user_data = json.loads(user_data)
            telegram_id = user_data.get('id')
            username = user_data.get('username')
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')

            if not telegram_id:
                return JsonResponse({'result': 'error', 'error_message': 'Missing user parameters'}, status=400)

            # Determine the referrer ID if present
            referred_by_id = None
            if start_param and start_param.startswith('ref_'):
                referred_by_id = int(start_param.split('_')[1])

            # Create or get the user
            user, created, referred_by_telegram_id = register_user_func_params(
                user_telegram_id=telegram_id,
                user_username_tg=username,
                user_first_name=first_name,
                user_last_name=last_name,
                referred_by_id=referred_by_id
            )

            logger.info(f"TelegramWebAppAuthView - User {'created' if created else 'logged in'} successfully. Telegram ID: {telegram_id}")

            # Generate JWT token
            jwt_token = user.get_jwt_token()
            response = JsonResponse({'result': 'success'})
            response.set_cookie('jwt_token', jwt_token['access'], httponly=True, secure=True, max_age=81000)

            try:
                if created:
                    # Сохранение нового пользователя в кэш
                    new_user = {
                        'id': user.id, 
                        'telegram_id': telegram_id, 
                        'username': username, 
                        'referred_by_telegram_id': referred_by_telegram_id
                    }
                    new_users = cache.get('new_users', [])
                    new_users.append(new_user)
                    cache.set('new_users', new_users, timeout=60*5)
                    print(new_users)
            except Exception as e:
                pass

            return response
        except Exception as e:
            logger.error(f"TelegramWebAppAuthView - An error occurred while parsing request: {str(e)}")
            return JsonResponse({'result': 'error', 'error_message': 'Invalid request format'}, status=400)


# Telegram Bot Authentication
class TelegramLoginView(APIView):
    def get(self, request, *args, **kwargs):
        auth_date = request.GET.get('auth_date')
        first_name = request.GET.get('first_name')
        hash = request.GET.get('hash')
        telegram_id = request.GET.get('id')
        last_name = request.GET.get('last_name')
        photo_url = request.GET.get('photo_url')
        username = request.GET.get('username')

        logger.debug(f"TelegramLoginView - Received data: auth_date={auth_date}, first_name={first_name}, hash={hash}, telegram_id={telegram_id}, last_name={last_name}, photo_url={photo_url}, username={username}")

        if not self.check_auth(request.GET):
            logger.error("TelegramLoginView - Invalid authentication data")
            return Response({'result': 'error', 'error_message': 'Invalid data'}, status=400)

        try:
            user, created, referred_by_telegram_id = User.objects.create_user(
                telegram_id=telegram_id,
                username_tg=username,
                first_name=first_name,
                last_name=last_name,
            )

            # Generate JWT token
            jwt_token = user.get_jwt_token()
            response = redirect('/api/v1/wallet/')
            response.set_cookie('jwt_token', jwt_token['access'], httponly=True, secure=True, max_age=81000)

            logger.info(f"TelegramLoginView - User {'created' if created else 'logged in'} successfully. Telegram ID: {telegram_id}")

            return response
        except Exception as e:
            logger.error(f"TelegramLoginView - An error occurred during user registration or login: {str(e)}")
            return Response({'result': 'error', 'error_message': str(e)}, status=500)

    def check_auth(self, data):
        """Check if the request is valid based on Telegram's auth mechanism."""
        auth_date = data.get('auth_date')
        user_id = data.get('id')
        received_hash = data.get('hash')

        # Create the check string
        check_string = "\n".join([f"{key}={value}" for key, value in sorted(data.items()) if key != 'hash'])

        secret_key = hashlib.sha256(config('TELEGRAM_BOT_TOKEN').encode()).digest()
        computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

        logger.debug(f"TelegramLoginView - Computed hash: {computed_hash}, Provided hash: {received_hash}")

        if not constant_time_compare(computed_hash, received_hash):
            logger.error("TelegramLoginView - Hash mismatch")
            return False

        if time.time() - int(auth_date) > 86400:  # Check if the auth_date is not older than 24 hours
            logger.error("TelegramLoginView - Authentication date expired")
            return False

        return True


# User Registration API
class RegisterUserView(generics.CreateAPIView):
    """
    API view for registering Telegram users.
    """
    authentication_classes = [FullPermissionsJWTAuthentication]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user registration.
        """
        try:
            telegram_id = request.data.get('telegram_id')
            username_tg = request.data.get('username_tg', None)
            first_name = request.data.get('first_name', None)
            last_name = request.data.get('last_name', None)
            
            if not telegram_id:
                logger.error("RegisterUserView - Missing telegram_id in request data")
                return Response({'result': 'error', 'error_message': 'Missing telegram_id in request data'},
                                status=status.HTTP_400_BAD_REQUEST)

            referred_by_id = request.data.get('referred_by_id')

            with transaction.atomic():
                user, created, referred_by_telegram_id = User.objects.create_user(
                    telegram_id=telegram_id,
                    username_tg=username_tg,
                    first_name=first_name,
                    last_name=last_name,
                    referred_by_id=referred_by_id,
                )

                if not created:
                    jwt_token = user.get_jwt_token()
                    logger.info(f"RegisterUserView - User already exists. Telegram ID: {telegram_id}")
                    return Response({'result': 'success', 'data': {'created': created, 'token': jwt_token, 'beta': user.has_beta_access, 'alpha': user.has_alpha_access}},
                                    status=status.HTTP_200_OK)
                else:
                    jwt_token = user.get_jwt_token()

                    # Bot detection logic
                    if detect_bot(telegram_id, referred_by_id):
                        user.is_bot_suspected = True
                        user.save()
                        referred_by_telegram_id = None

                    logger.info(f"RegisterUserView - User registered successfully. Telegram ID: {telegram_id}")
                    return Response({'result': 'success', 'data': {'created': created, 'token': jwt_token, 'beta': user.has_beta_access, 'alpha': user.has_alpha_access, 'referred_by_telegram_id': referred_by_telegram_id}},
                                    status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"RegisterUserView - An error occurred during user registration: {traceback.format_exc()}")
            return Response({'result': 'error', 'error_message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Check Authentication
class CheckAuthView(APIView):
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'result': 'success', 'username': user.username_tg, 'telegram_id': user.telegram_id})


# Logout
class TelegramLogoutView(APIView):
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = redirect('/api/v1/auth/')  # Redirect to auth page
        response.delete_cookie('jwt_token')
        return response


# User Profile
class UserProfileView(APIView):
    authentication_classes = [BetaAccessJWTAuthentication]
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
            'is_bot_suspected': user.is_bot_suspected,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        # TODO: Implement profile update logic
        return Response({'message': 'Profile updated'}, status=status.HTTP_200_OK)


# EVM Address Management
class EVMAddressView(APIView):
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add EVM address to user"""
        try:
            user = request.user
            chain = request.data.get('chain')  # 'ethereum' or 'base'
            address = request.data.get('address')

            if not chain or not address:
                return Response({'result': 'error', 'error_message': 'Chain and address are required'}, 
                               status=status.HTTP_400_BAD_REQUEST)

            if chain == 'ethereum':
                success = User.objects.add_ethereum_address(user, address)
            elif chain == 'base':
                success = User.objects.add_base_address(user, address)
            else:
                return Response({'result': 'error', 'error_message': 'Invalid chain'}, 
                               status=status.HTTP_400_BAD_REQUEST)

            if success:
                return Response({'result': 'success', 'message': f'{chain.title()} address added successfully'}, 
                               status=status.HTTP_200_OK)
            else:
                return Response({'result': 'error', 'error_message': 'Address already belongs to another user'}, 
                               status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"EVMAddressView - An error occurred: {str(e)}")
            return Response({'result': 'error', 'error_message': str(e)}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# EVM Wallet Registration
class EVMWalletRegistrationView(APIView):
    """
    API endpoint for users to register their EVM wallet address.
    Users can register or update their wallet address using JWT authentication.
    """
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Register or update EVM wallet address for authenticated user.
        
        Expected payload:
        {
            "chain": "ethereum" | "base",
            "address": "0x..."
        }
        """
        try:
            user = request.user
            chain = request.data.get('chain')
            address = request.data.get('address')

            # Validate required fields
            if not chain or not address:
                return Response({
                    'result': 'error', 
                    'error_message': 'Chain and address are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate chain - get from database
            try:
                evm_chain = EVMChain.objects.get(name__iexact=chain, is_active=True)
            except EVMChain.DoesNotExist:
                # Get list of supported chains for error message
                supported_chains = list(EVMChain.objects.filter(is_active=True).values_list('name', flat=True))
                return Response({
                    'result': 'error', 
                    'error_message': f'Invalid or inactive chain. Supported chains: {", ".join(supported_chains)}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate address format
            if not validate_evm_address(address):
                return Response({
                    'result': 'error', 
                    'error_message': 'Invalid EVM address format'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if address already belongs to another user
            existing_user = None
            if evm_chain.name.lower() == 'ethereum':
                existing_user = User.objects.filter(ethereum_address=address).exclude(id=user.id).first()
            elif evm_chain.name.lower() == 'base':
                existing_user = User.objects.filter(base_address=address).exclude(id=user.id).first()

            if existing_user:
                return Response({
                    'result': 'error', 
                    'error_message': 'This address is already registered to another user'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update user's address based on chain
            old_address = None
            if evm_chain.name.lower() == 'ethereum':
                old_address = user.ethereum_address
                user.ethereum_address = address
            elif evm_chain.name.lower() == 'base':
                old_address = user.base_address
                user.base_address = address

            user.save()

            # Prepare response
            response_data = {
                'result': 'success',
                'message': f'{evm_chain.name} wallet address {"updated" if old_address else "registered"} successfully',
                'data': {
                    'chain': evm_chain.name,
                    'chain_id': evm_chain.chain_id,
                    'address': address,
                    'old_address': old_address,
                    'user_id': user.id,
                    'telegram_id': user.telegram_id,
                    'chain_info': {
                        'name': evm_chain.name,
                        'chain_id': evm_chain.chain_id,
                        'native_currency': evm_chain.native_currency_symbol,
                        'is_testnet': evm_chain.is_testnet
                    }
                }
            }

            logger.info(f"EVMWalletRegistrationView - User {user.telegram_id} {'updated' if old_address else 'registered'} {chain} address: {address}")
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"EVMWalletRegistrationView - An error occurred: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Get current wallet addresses for authenticated user.
        """
        try:
            user = request.user
            
            response_data = {
                'result': 'success',
                'data': {
                    'user_id': user.id,
                    'telegram_id': user.telegram_id,
                    'ethereum_address': user.ethereum_address,
                    'base_address': user.base_address,
                    'has_ethereum': bool(user.ethereum_address),
                    'has_base': bool(user.base_address)
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"EVMWalletRegistrationView GET - An error occurred: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Supported Networks
class SupportedNetworksView(APIView):
    """
    API endpoint to get list of supported EVM networks.
    """
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get list of supported EVM networks.
        """
        try:
            networks = EVMChain.objects.filter(is_active=True).order_by('chain_id')
            
            networks_data = []
            for network in networks:
                networks_data.append({
                    'name': network.name,
                    'chain_id': network.chain_id,
                    'native_currency_symbol': network.native_currency_symbol,
                    'native_currency_name': network.native_currency_name,
                    'is_testnet': network.is_testnet,
                    'block_time_seconds': network.block_time_seconds,
                    'gas_price_gwei': float(network.gas_price_gwei),
                    'explorer_url': network.explorer_url
                })
            
            response_data = {
                'result': 'success',
                'data': {
                    'networks': networks_data,
                    'total_count': len(networks_data)
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"SupportedNetworksView - An error occurred: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# User Cooldowns
class UserCooldownView(APIView):
    authentication_classes = [BetaAccessJWTAuthentication]
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


# Admin Views
class AdminUserListView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.all()
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username_tg': user.username_tg,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'has_beta_access': user.has_beta_access,
                'has_alpha_access': user.has_alpha_access,
                'is_bot_suspected': user.is_bot_suspected,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            })
        return Response({'users': user_data}, status=status.HTTP_200_OK)


class AdminUserDetailView(APIView):
    authentication_classes = [AdminJWTAuthentication]
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
                'ethereum_address': user.ethereum_address,
                'base_address': user.base_address,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'has_beta_access': user.has_beta_access,
                'has_alpha_access': user.has_alpha_access,
                'is_bot_suspected': user.is_bot_suspected,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# Get New Users (for admin monitoring)
class GetNewUsersAPIView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Получение новых пользователей из кэша
            new_users = cache.get('new_users', [])

            # Очистка кэша
            cache.set('new_users', [])
            if len(new_users) > 0:
                logger.info(f"Retrieved {len(new_users)} new users from cache")

            return JsonResponse({'result': 'success', 'data': new_users}, status=200)
        except Exception as e:
            logger.error(f"Error retrieving new users from cache: {str(e)}")
            return JsonResponse({'result': 'error', 'error_message': 'Internal server error'}, status=500)


class CustomTokenObtainPairView(APIView):
    """
    Custom JWT token generation for any user by telegram_id.
    No authentication required - for development/testing purposes.
    """
    authentication_classes = []  # No authentication required
    permission_classes = []      # No permissions required

    def post(self, request, *args, **kwargs):
        """
        Generate JWT tokens for a user by telegram_id.
        No authentication required - for development/testing purposes.
        """
        telegram_id = request.data.get('telegram_id')

        if not telegram_id:
            logger.error("CustomTokenObtainPairView - Missing telegram_id in request data")
            return Response({'error': 'Missing telegram_id in request data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            logger.error("CustomTokenObtainPairView - User not found")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate JWT tokens using the user's method
        jwt_tokens = user.get_jwt_token()

        # Add user info to response
        response_data = {
            'access': jwt_tokens['access'],
            'refresh': jwt_tokens['refresh'],
            'user_info': {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username_tg': user.username_tg,
                'is_staff': user.is_staff,
                'has_alpha_access': user.has_alpha_access,
                'has_beta_access': user.has_beta_access,
                'full_permissions_api': user.full_permissions_api,
            }
        }

        logger.info(f"CustomTokenObtainPairView - JWT tokens generated successfully for user {telegram_id}")
        return Response(response_data, status=status.HTTP_200_OK)