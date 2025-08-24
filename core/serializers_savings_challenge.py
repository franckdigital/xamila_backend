"""
Serializers pour le module Challenge Épargne
Sérialisation des données pour l'API REST
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models_savings_challenge import (
    SavingsChallenge, ChallengeParticipation, SavingsDeposit,
    SavingsGoal, SavingsAccount, ChallengeLeaderboard
)

User = get_user_model()


class SavingsChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer pour les défis d'épargne
    """
    
    # Champs calculés
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    participants_count = serializers.SerializerMethodField()
    total_saved = serializers.SerializerMethodField()
    
    # Champs de création
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    class Meta:
        model = SavingsChallenge
        fields = [
            'id', 'title', 'description', 'short_description',
            'challenge_type', 'category', 'target_amount', 'minimum_deposit',
            'duration_days', 'reward_points', 'reward_percentage',
            'max_participants', 'is_public', 'status',
            'start_date', 'end_date', 'created_at', 'updated_at',
            'created_by_name', 'is_active', 'days_remaining',
            'participants_count', 'total_saved'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Nombre de participants actifs"""
        return getattr(obj, 'participants_count', 
                      obj.participations.filter(status='ACTIVE').count())
    
    def get_total_saved(self, obj):
        """Montant total épargné dans ce défi"""
        return getattr(obj, 'total_saved', 
                      obj.participations.aggregate(
                          total=serializers.models.Sum('total_saved')
                      )['total'] or Decimal('0.00'))


class ChallengeParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les participations aux défis
    """
    
    # Informations du défi
    challenge_title = serializers.CharField(
        source='challenge.title', read_only=True
    )
    challenge_type = serializers.CharField(
        source='challenge.challenge_type', read_only=True
    )
    challenge_target = serializers.DecimalField(
        source='challenge.target_amount', max_digits=15, decimal_places=2, read_only=True
    )
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    
    # Champs calculés
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    effective_target = serializers.SerializerMethodField()
    
    class Meta:
        model = ChallengeParticipation
        fields = [
            'id', 'user', 'challenge', 'status', 'personal_target',
            'total_saved', 'deposits_count', 'current_streak', 'longest_streak',
            'points_earned', 'bonus_earned', 'joined_at', 'completed_at',
            'last_deposit_at', 'updated_at',
            'challenge_title', 'challenge_type', 'challenge_target',
            'user_name', 'progress_percentage', 'is_completed', 'effective_target'
        ]
        read_only_fields = [
            'id', 'total_saved', 'deposits_count', 'current_streak',
            'longest_streak', 'points_earned', 'bonus_earned',
            'joined_at', 'completed_at', 'last_deposit_at', 'updated_at'
        ]
    
    def get_effective_target(self, obj):
        """Objectif effectif (personnel ou du défi)"""
        return obj.personal_target or obj.challenge.target_amount


class SavingsDepositSerializer(serializers.ModelSerializer):
    """
    Serializer pour les dépôts d'épargne
    """
    
    # Informations de la participation
    challenge_title = serializers.CharField(
        source='participation.challenge.title', read_only=True
    )
    user_name = serializers.CharField(
        source='participation.user.full_name', read_only=True
    )
    
    class Meta:
        model = SavingsDeposit
        fields = [
            'id', 'participation', 'amount', 'deposit_method', 'status',
            'transaction_reference', 'points_awarded', 'processed_at',
            'created_at', 'updated_at',
            'challenge_title', 'user_name'
        ]
        read_only_fields = [
            'id', 'points_awarded', 'processed_at', 'created_at', 'updated_at'
        ]
    
    def validate_amount(self, value):
        """Validation du montant minimum"""
        if value < Decimal('50'):
            raise serializers.ValidationError(
                "Le montant minimum est de 50 FCFA"
            )
        return value


class SavingsGoalSerializer(serializers.ModelSerializer):
    """
    Serializer pour les objectifs d'épargne
    """
    
    # Champs calculés
    progress_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    
    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'user', 'title', 'description', 'goal_type',
            'target_amount', 'current_amount', 'target_date', 'status',
            'created_at', 'updated_at',
            'user_name', 'progress_percentage', 'remaining_amount', 'days_remaining'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_remaining_amount(self, obj):
        """Montant restant à épargner"""
        return max(Decimal('0.00'), obj.target_amount - obj.current_amount)
    
    def get_days_remaining(self, obj):
        """Jours restants jusqu'à la date objectif"""
        if obj.target_date:
            from datetime import date
            delta = obj.target_date - date.today()
            return max(0, delta.days)
        return None
    
    def validate(self, data):
        """Validation des données"""
        target_amount = data.get('target_amount')
        current_amount = data.get('current_amount', Decimal('0.00'))
        
        if current_amount > target_amount:
            raise serializers.ValidationError(
                "Le montant actuel ne peut pas dépasser l'objectif"
            )
        
        return data


class SavingsAccountSerializer(serializers.ModelSerializer):
    """
    Serializer pour les comptes d'épargne
    """
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    
    # Informations de l'objectif lié
    goal_title = serializers.CharField(
        source='goal.title', read_only=True
    )
    
    class Meta:
        model = SavingsAccount
        fields = [
            'id', 'user', 'goal', 'account_number', 'account_name',
            'account_type', 'balance', 'interest_rate', 'status',
            'created_at', 'updated_at',
            'user_name', 'goal_title'
        ]
        read_only_fields = [
            'id', 'account_number', 'balance', 'created_at', 'updated_at'
        ]


class ChallengeLeaderboardSerializer(serializers.ModelSerializer):
    """
    Serializer pour le classement des défis
    """
    
    # Informations du participant
    user_name = serializers.CharField(
        source='participation.user.full_name', read_only=True
    )
    user_avatar = serializers.CharField(
        source='participation.user.avatar', read_only=True
    )
    
    # Statistiques de participation
    total_saved = serializers.DecimalField(
        source='participation.total_saved', max_digits=15, decimal_places=2, read_only=True
    )
    deposits_count = serializers.IntegerField(
        source='participation.deposits_count', read_only=True
    )
    current_streak = serializers.IntegerField(
        source='participation.current_streak', read_only=True
    )
    points_earned = serializers.IntegerField(
        source='participation.points_earned', read_only=True
    )
    progress_percentage = serializers.DecimalField(
        source='participation.progress_percentage', max_digits=5, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = ChallengeLeaderboard
        fields = [
            'id', 'rank', 'score', 'calculated_at',
            'user_name', 'user_avatar', 'total_saved', 'deposits_count',
            'current_streak', 'points_earned', 'progress_percentage'
        ]
        read_only_fields = ['id', 'calculated_at']


class SavingsStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques d'épargne
    """
    
    total_saved = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_points = serializers.IntegerField()
    active_challenges = serializers.IntegerField()
    completed_challenges = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    average_deposit = serializers.DecimalField(max_digits=10, decimal_places=2)
    savings_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class ChallengeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de défis (admin)
    """
    
    class Meta:
        model = SavingsChallenge
        fields = [
            'title', 'description', 'short_description', 'challenge_type',
            'category', 'target_amount', 'minimum_deposit', 'duration_days',
            'reward_points', 'reward_percentage', 'max_participants',
            'is_public', 'start_date', 'end_date'
        ]
    
    def validate(self, data):
        """Validation des données de création"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début"
            )
        
        target_amount = data.get('target_amount')
        minimum_deposit = data.get('minimum_deposit')
        
        if minimum_deposit and target_amount and minimum_deposit > target_amount:
            raise serializers.ValidationError(
                "Le dépôt minimum ne peut pas dépasser l'objectif"
            )
        
        return data


class DepositCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de dépôts
    """
    
    class Meta:
        model = SavingsDeposit
        fields = ['amount', 'deposit_method', 'transaction_reference']
    
    def validate_amount(self, value):
        """Validation du montant"""
        if value < Decimal('50'):
            raise serializers.ValidationError(
                "Le montant minimum est de 50 FCFA"
            )
        if value > Decimal('10000000'):  # 10M FCFA
            raise serializers.ValidationError(
                "Le montant maximum est de 10,000,000 FCFA"
            )
        return value


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'objectifs
    """
    
    class Meta:
        model = SavingsGoal
        fields = [
            'title', 'description', 'goal_type', 'target_amount',
            'target_date'
        ]
    
    def validate_target_amount(self, value):
        """Validation du montant objectif"""
        if value < Decimal('1000'):
            raise serializers.ValidationError(
                "L'objectif minimum est de 1,000 FCFA"
            )
        return value
    
    def validate_target_date(self, value):
        """Validation de la date objectif"""
        if value:
            from datetime import date
            if value <= date.today():
                raise serializers.ValidationError(
                    "La date objectif doit être dans le futur"
                )
        return value


class AccountCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de comptes d'épargne
    """
    
    class Meta:
        model = SavingsAccount
        fields = ['account_name', 'account_type', 'goal', 'interest_rate']
    
    def validate_interest_rate(self, value):
        """Validation du taux d'intérêt"""
        if value < Decimal('0'):
            raise serializers.ValidationError(
                "Le taux d'intérêt ne peut pas être négatif"
            )
        if value > Decimal('20'):
            raise serializers.ValidationError(
                "Le taux d'intérêt ne peut pas dépasser 20%"
            )
        return value
