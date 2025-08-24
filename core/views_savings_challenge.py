"""
Vues API pour le module Challenge Épargne
Endpoints REST pour la gamification de l'épargne
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models_savings_challenge import (
    SavingsChallenge, ChallengeParticipation, SavingsDeposit,
    SavingsGoal, SavingsAccount, ChallengeLeaderboard
)
from .serializers_savings_challenge import (
    SavingsChallengeSerializer, ChallengeParticipationSerializer,
    SavingsDepositSerializer, SavingsGoalSerializer,
    SavingsAccountSerializer, ChallengeLeaderboardSerializer
)


class SavingsChallengeListView(generics.ListCreateAPIView):
    """
    Liste des défis d'épargne disponibles
    GET: Récupère tous les défis actifs
    POST: Crée un nouveau défi (admin seulement)
    """
    serializer_class = SavingsChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SavingsChallenge.objects.filter(status='ACTIVE')
        
        # Filtres
        category = self.request.query_params.get('category')
        challenge_type = self.request.query_params.get('type')
        
        if category:
            queryset = queryset.filter(category=category)
        if challenge_type:
            queryset = queryset.filter(challenge_type=challenge_type)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Seuls les admins peuvent créer des défis
        if not self.request.user.role in ['ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied("Seuls les administrateurs peuvent créer des défis")
        
        serializer.save(created_by=self.request.user)


class SavingsChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un défi d'épargne spécifique
    """
    queryset = SavingsChallenge.objects.all()
    serializer_class = SavingsChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        challenge = super().get_object()
        
        # Ajouter des statistiques au défi
        challenge.participants_count = challenge.participations.filter(
            status='ACTIVE'
        ).count()
        
        challenge.total_saved = challenge.participations.filter(
            status__in=['ACTIVE', 'COMPLETED']
        ).aggregate(
            total=Sum('total_saved')
        )['total'] or Decimal('0.00')
        
        return challenge


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_challenge(request, challenge_id):
    """
    Rejoindre un défi d'épargne
    """
    try:
        challenge = SavingsChallenge.objects.get(id=challenge_id, status='ACTIVE')
    except SavingsChallenge.DoesNotExist:
        return Response(
            {'error': 'Défi introuvable ou inactif'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si l'utilisateur participe déjà
    existing_participation = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).first()
    
    if existing_participation:
        return Response(
            {'error': 'Vous participez déjà à ce défi'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier les limites de participants
    if challenge.max_participants:
        current_participants = challenge.participations.filter(
            status='ACTIVE'
        ).count()
        
        if current_participants >= challenge.max_participants:
            return Response(
                {'error': 'Le nombre maximum de participants est atteint'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Créer la participation
    participation_data = request.data.copy()
    participation_data['user'] = request.user.id
    participation_data['challenge'] = challenge.id
    
    serializer = ChallengeParticipationSerializer(data=participation_data)
    if serializer.is_valid():
        participation = serializer.save()
        return Response(
            ChallengeParticipationSerializer(participation).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChallengeParticipationsView(generics.ListAPIView):
    """
    Participations aux défis de l'utilisateur connecté
    """
    serializer_class = ChallengeParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChallengeParticipation.objects.filter(
            user=self.request.user
        ).select_related('challenge').order_by('-joined_at')


class ChallengeParticipationDetailView(generics.RetrieveUpdateAPIView):
    """
    Détails d'une participation à un défi
    """
    serializer_class = ChallengeParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChallengeParticipation.objects.filter(
            user=self.request.user
        ).select_related('challenge')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def make_deposit(request, participation_id):
    """
    Effectuer un dépôt dans le cadre d'un défi
    """
    try:
        participation = ChallengeParticipation.objects.get(
            id=participation_id,
            user=request.user,
            status='ACTIVE'
        )
    except ChallengeParticipation.DoesNotExist:
        return Response(
            {'error': 'Participation introuvable ou inactive'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que le défi est encore actif
    if not participation.challenge.is_active:
        return Response(
            {'error': 'Le défi n\'est plus actif'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valider le montant minimum
    amount = Decimal(str(request.data.get('amount', 0)))
    if amount < participation.challenge.minimum_deposit:
        return Response(
            {'error': f'Le montant minimum est de {participation.challenge.minimum_deposit} FCFA'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer le dépôt
    deposit_data = request.data.copy()
    deposit_data['participation'] = participation.id
    
    serializer = SavingsDepositSerializer(data=deposit_data)
    if serializer.is_valid():
        deposit = serializer.save()
        
        # Calculer les points accordés
        base_points = int(amount / 1000)  # 1 point par 1000 FCFA
        streak_bonus = participation.current_streak * 2
        deposit.points_awarded = base_points + streak_bonus
        deposit.save()
        
        return Response(
            SavingsDepositSerializer(deposit).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingsDepositListView(generics.ListAPIView):
    """
    Historique des dépôts de l'utilisateur
    """
    serializer_class = SavingsDepositSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavingsDeposit.objects.filter(
            participation__user=self.request.user
        ).select_related('participation__challenge').order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def challenge_leaderboard(request, challenge_id):
    """
    Classement d'un défi spécifique
    """
    try:
        challenge = SavingsChallenge.objects.get(id=challenge_id)
    except SavingsChallenge.DoesNotExist:
        return Response(
            {'error': 'Défi introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Récupérer le classement
    leaderboard = ChallengeLeaderboard.objects.filter(
        challenge=challenge
    ).select_related('participation__user').order_by('rank')
    
    serializer = ChallengeLeaderboardSerializer(leaderboard, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_leaderboard(request, challenge_id):
    """
    Mettre à jour le classement d'un défi (admin seulement)
    """
    if not request.user.role in ['ADMIN', 'SUPPORT']:
        return Response(
            {'error': 'Permission refusée'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        challenge = SavingsChallenge.objects.get(id=challenge_id)
    except SavingsChallenge.DoesNotExist:
        return Response(
            {'error': 'Défi introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Supprimer l'ancien classement
    ChallengeLeaderboard.objects.filter(challenge=challenge).delete()
    
    # Calculer le nouveau classement
    participations = ChallengeParticipation.objects.filter(
        challenge=challenge,
        status__in=['ACTIVE', 'COMPLETED']
    ).order_by('-total_saved', '-points_earned')
    
    # Créer les nouvelles entrées de classement
    leaderboard_entries = []
    for rank, participation in enumerate(participations, 1):
        # Calculer le score basé sur plusieurs facteurs
        progress_score = participation.progress_percentage
        streak_score = participation.longest_streak * 5
        consistency_score = participation.deposits_count * 2
        
        total_score = progress_score + streak_score + consistency_score
        
        leaderboard_entries.append(
            ChallengeLeaderboard(
                challenge=challenge,
                participation=participation,
                rank=rank,
                score=Decimal(str(total_score))
            )
        )
    
    ChallengeLeaderboard.objects.bulk_create(leaderboard_entries)
    
    return Response({'message': 'Classement mis à jour avec succès'})


# Vues pour les objectifs d'épargne personnels

class SavingsGoalListView(generics.ListCreateAPIView):
    """
    Objectifs d'épargne de l'utilisateur
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavingsGoal.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingsGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un objectif d'épargne
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)


# Vues pour les comptes d'épargne

class SavingsAccountListView(generics.ListCreateAPIView):
    """
    Comptes d'épargne de l'utilisateur
    """
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavingsAccount.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Générer un numéro de compte unique
        import random
        import string
        
        account_number = ''.join(random.choices(string.digits, k=10))
        while SavingsAccount.objects.filter(account_number=account_number).exists():
            account_number = ''.join(random.choices(string.digits, k=10))
        
        serializer.save(
            user=self.request.user,
            account_number=account_number
        )


class SavingsAccountDetailView(generics.RetrieveUpdateAPIView):
    """
    Détails d'un compte d'épargne
    """
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavingsAccount.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_savings_dashboard(request):
    """
    Dashboard d'épargne de l'utilisateur
    """
    user = request.user
    
    # Statistiques générales
    active_participations = ChallengeParticipation.objects.filter(
        user=user,
        status='ACTIVE'
    )
    
    total_saved_challenges = active_participations.aggregate(
        total=Sum('total_saved')
    )['total'] or Decimal('0.00')
    
    total_points = active_participations.aggregate(
        total=Sum('points_earned')
    )['total'] or 0
    
    # Comptes d'épargne
    accounts = SavingsAccount.objects.filter(user=user, status='ACTIVE')
    total_balance = accounts.aggregate(
        total=Sum('balance')
    )['total'] or Decimal('0.00')
    
    # Objectifs d'épargne
    goals = SavingsGoal.objects.filter(user=user, status='ACTIVE')
    completed_goals = goals.filter(
        current_amount__gte=models.F('target_amount')
    ).count()
    
    # Activité récente
    recent_deposits = SavingsDeposit.objects.filter(
        participation__user=user,
        status='CONFIRMED'
    ).order_by('-created_at')[:5]
    
    dashboard_data = {
        'summary': {
            'total_saved_challenges': total_saved_challenges,
            'total_balance_accounts': total_balance,
            'total_points': total_points,
            'active_challenges': active_participations.count(),
            'active_goals': goals.count(),
            'completed_goals': completed_goals,
        },
        'active_participations': ChallengeParticipationSerializer(
            active_participations, many=True
        ).data,
        'savings_accounts': SavingsAccountSerializer(
            accounts, many=True
        ).data,
        'savings_goals': SavingsGoalSerializer(
            goals, many=True
        ).data,
        'recent_deposits': SavingsDepositSerializer(
            recent_deposits, many=True
        ).data,
    }
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def savings_analytics(request):
    """
    Analytics d'épargne pour l'utilisateur
    """
    user = request.user
    
    # Période d'analyse (30 derniers jours par défaut)
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Dépôts par jour
    daily_deposits = SavingsDeposit.objects.filter(
        participation__user=user,
        status='CONFIRMED',
        created_at__gte=start_date
    ).extra(
        select={'day': 'DATE(created_at)'}
    ).values('day').annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    ).order_by('day')
    
    # Progression des objectifs
    goals_progress = []
    for goal in SavingsGoal.objects.filter(user=user, status='ACTIVE'):
        goals_progress.append({
            'goal': SavingsGoalSerializer(goal).data,
            'progress_percentage': goal.progress_percentage,
            'remaining_amount': goal.target_amount - goal.current_amount,
        })
    
    # Statistiques par défi
    challenge_stats = []
    for participation in ChallengeParticipation.objects.filter(
        user=user,
        status__in=['ACTIVE', 'COMPLETED']
    ):
        challenge_stats.append({
            'challenge': SavingsChallengeSerializer(participation.challenge).data,
            'participation': ChallengeParticipationSerializer(participation).data,
            'deposits_last_30_days': participation.deposits.filter(
                status='CONFIRMED',
                created_at__gte=start_date
            ).count(),
        })
    
    analytics_data = {
        'period_days': days,
        'daily_deposits': list(daily_deposits),
        'goals_progress': goals_progress,
        'challenge_statistics': challenge_stats,
        'total_saved_period': sum(d['total_amount'] for d in daily_deposits),
        'average_deposit': sum(d['total_amount'] for d in daily_deposits) / len(daily_deposits) if daily_deposits else 0,
    }
    
    return Response(analytics_data)
