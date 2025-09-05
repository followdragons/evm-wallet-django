from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from .models import EVMChain, Token, Wallet, TokenBalance, Transaction, ReferralReward
import logging

logger = logging.getLogger(__name__)


class EVMChainListView(ListAPIView):
    """
    List all EVM chains
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return EVMChain.objects.filter(is_active=True)
    
    def list(self, request):
        chains = self.get_queryset()
        chain_data = []
        for chain in chains:
            chain_data.append({
                'id': chain.id,
                'name': chain.name,
                'chain_id': chain.chain_id,
                'native_currency_symbol': chain.native_currency_symbol,
                'native_currency_name': chain.native_currency_name,
                'is_testnet': chain.is_testnet,
            })
        return Response({'chains': chain_data}, status=status.HTTP_200_OK)


class EVMChainDetailView(RetrieveAPIView):
    """
    Get EVM chain details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, chain_id):
        try:
            chain = EVMChain.objects.get(id=chain_id, is_active=True)
            return Response({
                'id': chain.id,
                'name': chain.name,
                'chain_id': chain.chain_id,
                'explorer_url': chain.explorer_url,
                'native_currency_symbol': chain.native_currency_symbol,
                'native_currency_name': chain.native_currency_name,
                'is_testnet': chain.is_testnet,
                'block_time_seconds': chain.block_time_seconds,
                'gas_price_gwei': chain.gas_price_gwei,
            }, status=status.HTTP_200_OK)
        except EVMChain.DoesNotExist:
            return Response({'error': 'Chain not found'}, status=status.HTTP_404_NOT_FOUND)


class TokenListView(ListAPIView):
    """
    List all tokens
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Token.objects.filter(is_active=True)
    
    def list(self, request):
        tokens = self.get_queryset()
        token_data = []
        for token in tokens:
            token_data.append({
                'id': token.id,
                'name': token.name,
                'symbol': token.symbol,
                'address': token.address,
                'decimals': token.decimals,
                'chain': token.chain.name,
                'is_native': token.is_native,
                'is_verified': token.is_verified,
            })
        return Response({'tokens': token_data}, status=status.HTTP_200_OK)


class TokenDetailView(RetrieveAPIView):
    """
    Get token details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, token_id):
        try:
            token = Token.objects.get(id=token_id, is_active=True)
            return Response({
                'id': token.id,
                'name': token.name,
                'symbol': token.symbol,
                'address': token.address,
                'decimals': token.decimals,
                'chain': token.chain.name,
                'is_native': token.is_native,
                'is_verified': token.is_verified,
                'logo_url': token.logo_url,
                'description': token.description,
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)


class WalletListView(ListAPIView):
    """
    List user wallets
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user, is_active=True)
    
    def list(self, request):
        wallets = self.get_queryset()
        wallet_data = []
        for wallet in wallets:
            wallet_data.append({
                'id': wallet.id,
                'address': wallet.address,
                'chain': wallet.chain.name,
                'is_verified': wallet.is_verified,
                'created_at': wallet.created_at,
            })
        return Response({'wallets': wallet_data}, status=status.HTTP_200_OK)


class WalletDetailView(RetrieveAPIView):
    """
    Get wallet details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, wallet_id):
        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user, is_active=True)
            return Response({
                'id': wallet.id,
                'address': wallet.address,
                'chain': wallet.chain.name,
                'is_verified': wallet.is_verified,
                'created_at': wallet.created_at,
            }, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)


class WalletCreateView(CreateAPIView):
    """
    Create a new wallet
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement wallet creation logic
        return Response({'message': 'Wallet creation endpoint'}, status=status.HTTP_200_OK)


class TokenBalanceListView(ListAPIView):
    """
    List user token balances
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TokenBalance.objects.filter(wallet__user=self.request.user)
    
    def list(self, request):
        balances = self.get_queryset()
        balance_data = []
        for balance in balances:
            balance_data.append({
                'id': balance.id,
                'token': balance.token.symbol,
                'chain': balance.token.chain.name,
                'balance': balance.balance,
                'frozen_balance': balance.frozen_balance,
                'available_balance': balance.get_available_balance(),
                'last_updated': balance.last_updated,
            })
        return Response({'balances': balance_data}, status=status.HTTP_200_OK)


class TokenBalanceDetailView(RetrieveAPIView):
    """
    Get token balance details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, balance_id):
        try:
            balance = TokenBalance.objects.get(id=balance_id, wallet__user=request.user)
            return Response({
                'id': balance.id,
                'token': balance.token.symbol,
                'chain': balance.token.chain.name,
                'balance': balance.balance,
                'frozen_balance': balance.frozen_balance,
                'available_balance': balance.get_available_balance(),
                'last_updated': balance.last_updated,
            }, status=status.HTTP_200_OK)
        except TokenBalance.DoesNotExist:
            return Response({'error': 'Balance not found'}, status=status.HTTP_404_NOT_FOUND)


class TransactionListView(ListAPIView):
    """
    List user transactions
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def list(self, request):
        transactions = self.get_queryset()
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'id': transaction.id,
                'hash': transaction.hash,
                'type': transaction.transaction_type,
                'status': transaction.status,
                'token': transaction.token.symbol,
                'amount': transaction.amount,
                'from_address': transaction.from_address,
                'to_address': transaction.to_address,
                'created_at': transaction.created_at,
            })
        return Response({'transactions': transaction_data}, status=status.HTTP_200_OK)


class TransactionDetailView(RetrieveAPIView):
    """
    Get transaction details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=request.user)
            return Response({
                'id': transaction.id,
                'hash': transaction.hash,
                'type': transaction.transaction_type,
                'status': transaction.status,
                'token': transaction.token.symbol,
                'amount': transaction.amount,
                'from_address': transaction.from_address,
                'to_address': transaction.to_address,
                'gas_used': transaction.gas_used,
                'gas_price': transaction.gas_price,
                'gas_fee': transaction.gas_fee,
                'block_number': transaction.block_number,
                'created_at': transaction.created_at,
                'confirmed_at': transaction.confirmed_at,
            }, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


class TransferView(APIView):
    """
    Transfer tokens between addresses
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement transfer logic
        return Response({'message': 'Transfer endpoint'}, status=status.HTTP_200_OK)


class DepositView(APIView):
    """
    Deposit tokens to wallet
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement deposit logic
        return Response({'message': 'Deposit endpoint'}, status=status.HTTP_200_OK)


class WithdrawView(APIView):
    """
    Withdraw tokens from wallet
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement withdrawal logic
        return Response({'message': 'Withdraw endpoint'}, status=status.HTTP_200_OK)
