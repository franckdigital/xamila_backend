"""
Modèles spécialisés pour le challenge épargne
Gamification de l'épargne avec défis, objectifs et récompenses
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta, date

User = get_user_model()


class SavingsChallenge(models.Model):
    """
    Défis d'épargne disponibles
    """
    
    CHALLENGE_TYPES = [
        ('DAILY', 'Défi quotidien'),
        ('WEEKLY', 'Défi hebdomadaire'),
        ('MONTHLY', 'Défi mensuel'),
        ('QUARTERLY', 'Défi trimestriel'),
        ('SEMIANNUAL', 'Défi semestriel'),
        ('YEARLY', 'Défi annuel'),
        ('CUSTOM', 'Défi personnalisé'),
    ]
    
    CHALLENGE_CATEGORIES = [
        ('BEGINNER', 'Débutant'),
        ('INTERMEDIATE', 'Intermédiaire'),
        ('ADVANCED', 'Avancé'),
        ('EXPERT', 'Expert'),
        ('SPECIAL', 'Spécial'),
    ]
    
    CHALLENGE_STATUS = [
        ('DRAFT', 'Brouillon'),
        ('ACTIVE', 'Actif'),
        ('PAUSED', 'En pause'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations du défi
    title = models.CharField(max_length=200, verbose_name="Titre du défi")
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(
        max_length=500, verbose_name="Description courte"
    )
    
    # Type et catégorie
    challenge_type = models.CharField(
        max_length=20, choices=CHALLENGE_TYPES,
        verbose_name="Type de défi"
    )
    category = models.CharField(
        max_length=20, choices=CHALLENGE_CATEGORIES,
        verbose_name="Catégorie"
    )
    
    # Objectifs financiers
    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('100'))],
        verbose_name="Montant objectif (FCFA)"
    )
    minimum_deposit = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('50'))],
        verbose_name="Dépôt minimum (FCFA)"
    )
    
    # Durée
    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Durée en jours"
    )
    
    # Récompenses
    reward_points = models.PositiveIntegerField(
        default=0, verbose_name="Points de récompense"
    )
    reward_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Bonus de récompense (%)"
    )
    
    # Configuration
    max_participants = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name="Nombre maximum de participants"
    )
    is_public = models.BooleanField(
        default=True, verbose_name="Défi public"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=CHALLENGE_STATUS,
        default='DRAFT', verbose_name="Statut"
    )
    
    # Dates
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_challenges'
    )
    
    class Meta:
        verbose_name = "Défi d'épargne"
        verbose_name_plural = "Défis d'épargne"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_challenge_type_display()})"
    
    @property
    def is_active(self):
        """Vérifie si le défi est actuellement actif"""
        today = date.today()
        return (
            self.status == 'ACTIVE' and
            self.start_date <= today <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Calcule le nombre de jours restants"""
        if self.end_date:
            delta = self.end_date - date.today()
            return max(0, delta.days)
        return 0


class ChallengeParticipation(models.Model):
    """
    Participation d'un utilisateur à un défi d'épargne
    """
    
    PARTICIPATION_STATUS = [
        ('PENDING', 'En attente'),
        ('ACTIVE', 'Actif'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échoué'),
        ('WITHDRAWN', 'Retiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='challenge_participations'
    )
    challenge = models.ForeignKey(
        SavingsChallenge, on_delete=models.CASCADE,
        related_name='participations'
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=PARTICIPATION_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    
    # Objectifs personnalisés
    personal_target = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('100'))],
        verbose_name="Objectif personnel (FCFA)"
    )
    
    # Progression
    total_saved = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Total épargné (FCFA)"
    )
    deposits_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de dépôts"
    )
    
    # Statistiques
    current_streak = models.PositiveIntegerField(
        default=0, verbose_name="Série actuelle"
    )
    longest_streak = models.PositiveIntegerField(
        default=0, verbose_name="Plus longue série"
    )
    
    # Récompenses gagnées
    points_earned = models.PositiveIntegerField(
        default=0, verbose_name="Points gagnés"
    )
    bonus_earned = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Bonus gagné (FCFA)"
    )
    
    # Dates importantes
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_deposit_at = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participation au défi"
        verbose_name_plural = "Participations aux défis"
        ordering = ['-joined_at']
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.challenge.title}"
    
    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression"""
        target = self.personal_target or self.challenge.target_amount
        if target > 0:
            return min(100, (self.total_saved / target) * 100)
        return 0
    
    @property
    def is_completed(self):
        """Vérifie si l'objectif est atteint"""
        target = self.personal_target or self.challenge.target_amount
        return self.total_saved >= target


class SavingsDeposit(models.Model):
    """
    Dépôts effectués dans le cadre d'un défi d'épargne
    """
    
    DEPOSIT_STATUS = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('FAILED', 'Échec'),
        ('REFUNDED', 'Remboursé'),
    ]
    
    DEPOSIT_METHODS = [
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Virement bancaire'),
        ('CARD', 'Carte bancaire'),
        ('CASH', 'Espèces'),
        ('AUTOMATIC', 'Prélèvement automatique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    participation = models.ForeignKey(
        ChallengeParticipation, on_delete=models.CASCADE,
        related_name='deposits', blank=True, null=True
    )
    
    # Informations du dépôt
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('50'))],
        verbose_name="Montant (FCFA)"
    )
    deposit_method = models.CharField(
        max_length=20, choices=DEPOSIT_METHODS,
        verbose_name="Méthode de dépôt"
    )
    bank_name = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Nom de la banque"
    )
    
    # Statut et traitement
    status = models.CharField(
        max_length=20, choices=DEPOSIT_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    
    # Références externes
    transaction_reference = models.CharField(
        max_length=100, blank=True,
        verbose_name="Référence de transaction"
    )
    
    # Points et bonus
    points_awarded = models.PositiveIntegerField(
        default=0, verbose_name="Points attribués"
    )
    
    # Dates
    processed_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Date de traitement"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dépôt d'épargne"
        verbose_name_plural = "Dépôts d'épargne"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.amount} FCFA - {self.participation.user.full_name}"


class SavingsGoal(models.Model):
    """
    Objectifs d'épargne personnels des utilisateurs
    """
    
    GOAL_TYPES = [
        ('EMERGENCY_FUND', 'Fonds d\'urgence'),
        ('VACATION', 'Vacances'),
        ('EDUCATION', 'Éducation'),
        ('HOUSE', 'Achat immobilier'),
        ('CAR', 'Achat véhicule'),
        ('WEDDING', 'Mariage'),
        ('RETIREMENT', 'Retraite'),
        ('INVESTMENT', 'Investissement'),
        ('OTHER', 'Autre'),
    ]
    
    GOAL_STATUS = [
        ('ACTIVE', 'Actif'),
        ('COMPLETED', 'Terminé'),
        ('PAUSED', 'En pause'),
        ('CANCELLED', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='savings_goals'
    )
    
    # Informations de l'objectif
    title = models.CharField(max_length=200, verbose_name="Titre de l'objectif")
    description = models.TextField(blank=True, verbose_name="Description")
    goal_type = models.CharField(
        max_length=20, choices=GOAL_TYPES,
        verbose_name="Type d'objectif"
    )
    
    # Montants
    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('1000'))],
        verbose_name="Montant objectif (FCFA)"
    )
    current_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant actuel (FCFA)"
    )
    
    # Dates
    target_date = models.DateField(
        blank=True, null=True,
        verbose_name="Date objectif"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=GOAL_STATUS,
        default='ACTIVE', verbose_name="Statut"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Objectif d'épargne"
        verbose_name_plural = "Objectifs d'épargne"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression"""
        if self.target_amount > 0:
            return min(100, (self.current_amount / self.target_amount) * 100)
        return 0


class SavingsAccount(models.Model):
    """
    Comptes d'épargne virtuels des utilisateurs
    """
    
    ACCOUNT_TYPES = [
        ('BASIC', 'Compte de base'),
        ('PREMIUM', 'Compte premium'),
        ('CHALLENGE', 'Compte défi'),
        ('GOAL', 'Compte objectif'),
    ]
    
    ACCOUNT_STATUS = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('FROZEN', 'Gelé'),
        ('CLOSED', 'Fermé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='savings_accounts'
    )
    goal = models.OneToOneField(
        SavingsGoal, on_delete=models.CASCADE, blank=True, null=True,
        related_name='savings_account'
    )
    
    # Informations du compte
    account_number = models.CharField(
        max_length=20, unique=True,
        verbose_name="Numéro de compte"
    )
    account_name = models.CharField(
        max_length=200, verbose_name="Nom du compte"
    )
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES,
        verbose_name="Type de compte"
    )
    
    # Soldes
    balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Solde (FCFA)"
    )
    
    # Taux d'intérêt
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('20'))],
        verbose_name="Taux d'intérêt annuel (%)"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=ACCOUNT_STATUS,
        default='ACTIVE', verbose_name="Statut"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Compte d'épargne"
        verbose_name_plural = "Comptes d'épargne"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account_number} - {self.user.full_name}"


class ChallengeLeaderboard(models.Model):
    """
    Classement des participants aux défis
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    challenge = models.ForeignKey(
        SavingsChallenge, on_delete=models.CASCADE,
        related_name='leaderboard_entries'
    )
    participation = models.ForeignKey(
        ChallengeParticipation, on_delete=models.CASCADE,
        related_name='leaderboard_entries'
    )
    
    # Classement
    rank = models.PositiveIntegerField(verbose_name="Rang")
    score = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Score"
    )
    
    # Métadonnées
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Classement défi"
        verbose_name_plural = "Classements défis"
        ordering = ['challenge', 'rank']
        unique_together = ['challenge', 'participation']
    
    def __str__(self):
        return f"{self.challenge.title} - Rang {self.rank}"
