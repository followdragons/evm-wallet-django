import hashlib
import hmac
import json
import logging
import time
import traceback
from datetime import timedelta
from decimal import Decimal
from urllib.parse import unquote

import pytz
import requests
from decouple import config
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, UserProfile, UserCooldown
from .serializers import UserSerializer
from wallet.models import EVMChain, Token, Wallet, TokenBalance, Transaction, ReferralReward

logger = logging.getLogger(__name__)

def validate_evm_address(address):
    """Validate EVM address format"""
    if not address:
        return False
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

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
    JWT Authentication class to authenticate requests based on authorized FULL PERMISSIONS API requests.
    """

    def authenticate(self, request):
        """
        Custom authentication method.
        """
        # Call the parent class's authenticate method to perform basic JWT authentication
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

        # Check if we are in beta testing
        # general_config = GeneralConfig.objects.first()  # Assuming there's only one instance
        # if general_config and general_config.is_in_beta:
        #     # Check if the user has full API permissions
        #     if not user.has_beta_access:
        #         raise AuthenticationFailed('User does not have access to BETA')

        # Update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user, validated_token

class AlfaAccessJWTAuthentication(JWTAuthentication):
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

        # Check if we are in beta testing
        # general_config = GeneralConfig.objects.first()  # Assuming there's only one instance

        # if not user.has_alfa_access:
        #     raise AuthenticationFailed('User does not have access to ALFA')

        # Update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user, validated_token

class EVMWalletRegistrationView(APIView):
    """
    API view for registering EVM wallet addresses for authenticated users.
    """
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Register or update EVM wallet address for the authenticated user.
        """
        try:
            user = request.user
            chain_id = request.data.get('chain_id')
            address = request.data.get('address')

            if not chain_id or not address:
                return Response({
                    'result': 'error', 
                    'error_message': 'chain_id and address are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate chain
            try:
                chain = EVMChain.objects.get(chain_id=chain_id, is_active=True)
            except EVMChain.DoesNotExist:
                return Response({
                    'result': 'error', 
                    'error_message': 'Unsupported chain'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate address format
            if not validate_evm_address(address):
                return Response({
                    'result': 'error', 
                    'error_message': 'Invalid EVM address format'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if address is already registered to another user
            existing_wallet = Wallet.objects.filter(address=address).exclude(user=user).first()
            if existing_wallet:
                return Response({
                    'result': 'error', 
                    'error_message': 'Address already registered to another user'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update or create wallet
            wallet, created = Wallet.objects.get_or_create(
                user=user,
                chain=chain,
                defaults={'address': address}
            )

            if not created:
                wallet.address = address
                wallet.save()

            # Update user's address based on chain
            if chain.name.lower() == 'ethereum':
                user.ethereum_address = address
            elif chain.name.lower() == 'base':
                user.base_address = address
            
            user.save(update_fields=['ethereum_address', 'base_address'])

            logger.info(f"EVMWalletRegistrationView - Wallet {'created' if created else 'updated'} for user {user.id}: {address} on {chain.name}")

            return Response({
                'result': 'success',
                'data': {
                    'wallet_id': wallet.id,
                    'address': address,
                    'chain': chain.name,
                    'chain_id': chain.chain_id,
                    'created': created
                }
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"EVMWalletRegistrationView - Error: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Get user's registered wallets.
        """
        try:
            user = request.user
            wallets = Wallet.objects.filter(user=user).select_related('chain')
            
            wallet_data = []
            for wallet in wallets:
                wallet_data.append({
                    'wallet_id': wallet.id,
                    'address': wallet.address,
                    'chain': wallet.chain.name,
                    'chain_id': wallet.chain.chain_id,
                    'created_at': wallet.created_at.isoformat()
                })

            return Response({
                'result': 'success',
                'data': wallet_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"EVMWalletRegistrationView - Error: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SupportedNetworksView(APIView):
    """
    API view for getting supported blockchain networks.
    """
    authentication_classes = [BetaAccessJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get list of supported blockchain networks.
        """
        try:
            chains = EVMChain.objects.filter(is_active=True).order_by('name')
            
            networks_data = []
            for chain in chains:
                networks_data.append({
                    'chain_id': chain.chain_id,
                    'name': chain.name,
                    'symbol': chain.symbol,
                    'rpc_url': chain.rpc_url,
                    'explorer_url': chain.explorer_url,
                    'is_testnet': chain.is_testnet
                })

            return Response({
                'result': 'success',
                'data': networks_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"SupportedNetworksView - Error: {str(e)}")
            return Response({
                'result': 'error', 
                'error_message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebAppLoginView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            data = request.GET
            user_data = data.get('user')
            auth_date = data.get('auth_date')
            # query_id = data.get('query_id')
            received_hash = data.get('hash')
            start_param = data.get('start_param')

            if not user_data or not auth_date or not received_hash:
                response = JsonResponse({'result': 'error', 'error_message': 'Missing parameters'}, status=400)
                response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                response['Access-Control-Allow-Credentials'] = 'true'
                return response

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
                response = JsonResponse({'result': 'error', 'error_message': 'Invalid authentication data'}, status=400)
                response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                response['Access-Control-Allow-Credentials'] = 'true'
                return response

            # Check if auth_date is within 24 hours
            if time.time() - int(auth_date) > 86400:
                logger.error("TelegramWebAppAuthView - Authentication date expired")
                response = JsonResponse({'result': 'error', 'error_message': 'Authentication date expired'}, status=400)
                response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                response['Access-Control-Allow-Credentials'] = 'true'
                return response

            # Decode user data from JSON
            user_data = json.loads(user_data)
            telegram_id = user_data.get('id')
            username = user_data.get('username')

            if not telegram_id or not username:
                response = JsonResponse({'result': 'error', 'error_message': 'Missing user parameters'}, status=400)
                response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                response['Access-Control-Allow-Credentials'] = 'true'
                return response

            # Determine the referrer ID if present
            referred_by_id = None
            if start_param and start_param.startswith('ref_'):
                referred_by_id = int(start_param.split('_')[1])

            # Create or get the user
            user, created, referred_by_telegram_id = register_user_func_params(
                user_telegram_id=telegram_id,
                user_username_tg=username,
                referred_by_id=referred_by_id
            )

            logger.info(f"TelegramWebAppAuthView - User {'created' if created else 'logged in'} successfully. Telegram ID: {telegram_id}")

            # Generate JWT token
            jwt_token = user.get_jwt_token()
            response = JsonResponse({'result': 'success'})
            response.set_cookie('jwt_token', jwt_token['access'], httponly=True, secure=True, max_age=81000)
            
            # Add CORS headers
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Credentials'] = 'true'

            try:
                if created:
                    # Сохранение нового пользователя в кэш
                    new_user = {'id': user.id, 'telegram_id': telegram_id, 'username': username, 'referred_by_telegram_id': referred_by_telegram_id}
                    new_users = cache.get('new_users', [])
                    new_users.append(new_user)
                    cache.set('new_users', new_users, timeout=60*5)
                    print(new_users)
            except Exception as e:
                pass

            return response
        except Exception as e:
            logger.error(f"TelegramWebAppAuthView - An error occurred while parsing request: {str(e)}")
            response = JsonResponse({'result': 'error', 'error_message': 'Invalid request format'}, status=400)
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Credentials'] = 'true'
            return response

def register_user_func_params(user_telegram_id: int, user_username_tg: str, referred_by_id: int = None):
    try:
        with transaction.atomic():
            user, created, referred_by_telegram_id = User.objects.create_user(
                telegram_id=user_telegram_id,
                referred_by_id=referred_by_id,
                username_tg=user_username_tg,
            )

            if not created:
                logger.info(f"register_user_func - User already exists. Telegram ID: {user_telegram_id}")
                return user, created, None
            else:
                logger.info(f"register_user_func - User registered successfully. Telegram ID: {user_telegram_id}")
                return user, created, referred_by_telegram_id
    except Exception as e:
        logger.error(f"register_user_func - An error occurred during user registration: {traceback.format_exc()}")
        raise ValueError(f"{e}")

# Telegram Bot Authentication
@method_decorator(csrf_exempt, name='dispatch')
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
