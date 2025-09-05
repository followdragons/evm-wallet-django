from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'squad'

urlpatterns = [
    # Squad management
    path('squads/', views.SquadListView.as_view(), name='squad_list'),
    path('squads/<int:squad_id>/', views.SquadDetailView.as_view(), name='squad_detail'),
    path('squads/create/', views.SquadCreateView.as_view(), name='squad_create'),
    path('squads/<int:squad_id>/join/', views.SquadJoinView.as_view(), name='squad_join'),
    path('squads/<int:squad_id>/leave/', views.SquadLeaveView.as_view(), name='squad_leave'),
    
    # Squad membership
    path('squads/<int:squad_id>/members/', views.SquadMemberListView.as_view(), name='squad_members'),
    path('squads/<int:squad_id>/members/<int:user_id>/', views.SquadMemberDetailView.as_view(), name='squad_member_detail'),
    
    # Squad wallets and balances
    path('squads/<int:squad_id>/wallet/', views.SquadWalletView.as_view(), name='squad_wallet'),
    path('squads/<int:squad_id>/balances/', views.SquadBalanceListView.as_view(), name='squad_balances'),
    path('squads/<int:squad_id>/balances/<int:balance_id>/', views.SquadBalanceDetailView.as_view(), name='squad_balance_detail'),
    
    # Squad activities
    path('squads/<int:squad_id>/activities/', views.SquadActivityListView.as_view(), name='squad_activities'),
    
    
    # Token drops
    path('squads/<int:squad_id>/drops/', views.SquadDropListView.as_view(), name='squad_drops'),
    path('squads/<int:squad_id>/drops/create/', views.SquadDropCreateView.as_view(), name='squad_drop_create'),
    path('drops/<int:drop_id>/claim/', views.SquadDropClaimView.as_view(), name='squad_drop_claim'),
]
