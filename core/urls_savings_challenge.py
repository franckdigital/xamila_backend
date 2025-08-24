"""
URLs pour le module Challenge Épargne
Endpoints REST pour la gestion des défis d'épargne gamifiés
"""

from django.urls import path
from . import views_savings_challenge

app_name = 'savings_challenge'

urlpatterns = [
    # === SAVINGS CHALLENGES ===
    path('challenges/', views_savings_challenge.SavingsChallengeListView.as_view(), name='challenge-list'),
    path('challenges/<uuid:pk>/', views_savings_challenge.SavingsChallengeDetailView.as_view(), name='challenge-detail'),
    path('challenges/<uuid:challenge_id>/join/', views_savings_challenge.join_challenge, name='join-challenge'),
    path('challenges/<uuid:challenge_id>/leaderboard/', views_savings_challenge.challenge_leaderboard, name='challenge-leaderboard'),
    path('challenges/<uuid:challenge_id>/update-leaderboard/', views_savings_challenge.update_leaderboard, name='update-leaderboard'),
    
    # === CHALLENGE PARTICIPATIONS ===
    path('participations/', views_savings_challenge.UserChallengeParticipationsView.as_view(), name='participation-list'),
    path('participations/<uuid:pk>/', views_savings_challenge.ChallengeParticipationDetailView.as_view(), name='participation-detail'),
    path('participations/<uuid:participation_id>/deposit/', views_savings_challenge.make_deposit, name='make-deposit'),
    
    # === SAVINGS DEPOSITS ===
    path('deposits/', views_savings_challenge.SavingsDepositListView.as_view(), name='deposit-list'),
    
    # === SAVINGS GOALS ===
    path('goals/', views_savings_challenge.SavingsGoalListView.as_view(), name='goal-list'),
    path('goals/<uuid:pk>/', views_savings_challenge.SavingsGoalDetailView.as_view(), name='goal-detail'),
    
    # === SAVINGS ACCOUNTS ===
    path('accounts/', views_savings_challenge.SavingsAccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', views_savings_challenge.SavingsAccountDetailView.as_view(), name='account-detail'),
    
    # === DASHBOARD & ANALYTICS ===
    path('dashboard/', views_savings_challenge.user_savings_dashboard, name='savings-dashboard'),
    path('analytics/', views_savings_challenge.savings_analytics, name='savings-analytics'),
]
