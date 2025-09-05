from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from .models import Squad, SquadWallet, SquadTokenBalance, SquadMemberBalance, SquadActivity
import logging

logger = logging.getLogger(__name__)


class SquadListView(ListAPIView):
    """
    List all public squads
    """
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Squad.objects.filter(is_public=True, is_active=True)
    
    def list(self, request):
        squads = self.get_queryset()
        squad_data = []
        for squad in squads:
            squad_data.append({
                'id': squad.id,
                'name': squad.name,
                'description': squad.description,
                'owner': squad.owner.username_tg,
                'member_count': squad.get_member_count(),
                'max_members': squad.max_members,
                'created_at': squad.created_at,
            })
        return Response({'squads': squad_data}, status=status.HTTP_200_OK)


class SquadDetailView(RetrieveAPIView):
    """
    Get squad details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, squad_id):
        try:
            squad = Squad.objects.get(id=squad_id, is_active=True)
            return Response({
                'id': squad.id,
                'name': squad.name,
                'description': squad.description,
                'owner': squad.owner.username_tg,
                'member_count': squad.get_member_count(),
                'max_members': squad.max_members,
                'is_public': squad.is_public,
                'avatar_url': squad.avatar_url,
                'banner_url': squad.banner_url,
                'created_at': squad.created_at,
            }, status=status.HTTP_200_OK)
        except Squad.DoesNotExist:
            return Response({'error': 'Squad not found'}, status=status.HTTP_404_NOT_FOUND)


class SquadCreateView(CreateAPIView):
    """
    Create a new squad
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implement squad creation logic
        return Response({'message': 'Squad creation endpoint'}, status=status.HTTP_200_OK)


class SquadJoinView(APIView):
    """
    Join a squad
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, squad_id):
        # TODO: Implement squad join logic
        return Response({'message': 'Squad join endpoint'}, status=status.HTTP_200_OK)


class SquadLeaveView(APIView):
    """
    Leave a squad
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, squad_id):
        # TODO: Implement squad leave logic
        return Response({'message': 'Squad leave endpoint'}, status=status.HTTP_200_OK)


class SquadMemberListView(ListAPIView):
    """
    List squad members
    """
    permission_classes = [AllowAny]
    
    def get(self, request, squad_id):
        try:
            squad = Squad.objects.get(id=squad_id, is_active=True)
            members = []
            # Add owner
            members.append({
                'id': squad.owner.id,
                'username_tg': squad.owner.username_tg,
                'is_owner': True,
            })
            # Add regular members
            for member in squad.members.all():
                members.append({
                    'id': member.id,
                    'username_tg': member.username_tg,
                    'is_owner': False,
                })
            return Response({'members': members}, status=status.HTTP_200_OK)
        except Squad.DoesNotExist:
            return Response({'error': 'Squad not found'}, status=status.HTTP_404_NOT_FOUND)


class SquadMemberDetailView(RetrieveAPIView):
    """
    Get squad member details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, squad_id, user_id):
        # TODO: Implement squad member detail logic
        return Response({'message': 'Squad member detail endpoint'}, status=status.HTTP_200_OK)


class SquadWalletView(APIView):
    """
    Get squad wallet information
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, squad_id):
        # TODO: Implement squad wallet logic
        return Response({'message': 'Squad wallet endpoint'}, status=status.HTTP_200_OK)


class SquadBalanceListView(ListAPIView):
    """
    List squad token balances
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, squad_id):
        # TODO: Implement squad balance list logic
        return Response({'message': 'Squad balance list endpoint'}, status=status.HTTP_200_OK)


class SquadBalanceDetailView(RetrieveAPIView):
    """
    Get squad token balance details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, squad_id, balance_id):
        # TODO: Implement squad balance detail logic
        return Response({'message': 'Squad balance detail endpoint'}, status=status.HTTP_200_OK)


class SquadActivityListView(ListAPIView):
    """
    List squad activities
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, squad_id):
        # TODO: Implement squad activity list logic
        return Response({'message': 'Squad activity list endpoint'}, status=status.HTTP_200_OK)




class SquadDropListView(ListAPIView):
    """
    List squad token drops
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, squad_id):
        # TODO: Implement squad drop list logic
        return Response({'message': 'Squad drop list endpoint'}, status=status.HTTP_200_OK)


class SquadDropCreateView(CreateAPIView):
    """
    Create a squad token drop
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, squad_id):
        # TODO: Implement squad drop creation logic
        return Response({'message': 'Squad drop creation endpoint'}, status=status.HTTP_200_OK)


class SquadDropClaimView(APIView):
    """
    Claim a squad token drop
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, drop_id):
        # TODO: Implement squad drop claim logic
        return Response({'message': 'Squad drop claim endpoint'}, status=status.HTTP_200_OK)
