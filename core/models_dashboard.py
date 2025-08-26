from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
import uuid

User = get_user_model()

# Import des modèles existants pour éviter les conflits
def get_savings_challenge_model():
    """Import dynamique pour éviter les dépendances circulaires"""
    from .models_savings_challenge import SavingsChallenge
    return SavingsChallenge

class UserInvestment(models.Model):
    """Investissements de l'utilisateur dans les SGI"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    sgi = models.ForeignKey('SGI', on_delete=models.CASCADE)
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Montant investi en FCFA")
    current_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Valeur actuelle en FCFA")
    purchase_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_investments'
        verbose_name = 'Investissement Utilisateur'
        verbose_name_plural = 'Investissements Utilisateurs'
    
    def __str__(self):
        return f"{self.user.username} - {self.sgi.name}"
    
    @property
    def performance_percentage(self):
        """Calcule le pourcentage de performance"""
        if self.invested_amount > 0:
            return ((self.current_value - self.invested_amount) / self.invested_amount) * 100
        return 0
    
    @property
    def profit_loss(self):
        """Calcule le gain/perte"""
        return self.current_value - self.invested_amount

# SavingsChallenge est déjà défini dans models_savings_challenge.py
# On l'importe ici pour éviter les conflits
# from .models_savings_challenge import SavingsChallenge

class UserSavingsProgress(models.Model):
    """Progression de l'utilisateur dans les challenges d'épargne"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_progress')
    challenge = models.ForeignKey('SavingsChallenge', on_delete=models.CASCADE)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Montant épargné en FCFA")
    streak_days = models.IntegerField(default=0, help_text="Jours consécutifs d'épargne")
    last_saving_date = models.DateTimeField(null=True, blank=True)
    badges_earned = models.JSONField(default=list, help_text="Liste des badges obtenus")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_savings_progress'
        verbose_name = 'Progression Épargne'
        verbose_name_plural = 'Progressions Épargne'
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"
    
    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression"""
        if self.challenge.target_amount > 0:
            return (self.current_amount / self.challenge.target_amount) * 100
        return 0
    
    @property
    def rank(self):
        """Calcule le rang de l'utilisateur dans le challenge"""
        better_users = UserSavingsProgress.objects.filter(
            challenge=self.challenge,
            current_amount__gt=self.current_amount
        ).count()
        return better_users + 1

class DashboardTransaction(models.Model):
    """Transactions financières"""
    TRANSACTION_TYPES = [
        ('INVESTMENT', 'Investissement'),
        ('WITHDRAWAL', 'Retrait'),
        ('SAVINGS', 'Épargne'),
        ('DIVIDEND', 'Dividende'),
        ('FEE', 'Frais'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('PROCESSED', 'Traité'),
        ('CANCELLED', 'Annulé'),
        ('FAILED', 'Échoué'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Montant en FCFA")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(help_text="Description de la transaction")
    reference_id = models.CharField(max_length=100, unique=True, help_text="Référence unique")
    
    # Relations optionnelles
    sgi = models.ForeignKey('SGI', on_delete=models.SET_NULL, null=True, blank=True)
    investment = models.ForeignKey(UserInvestment, on_delete=models.SET_NULL, null=True, blank=True)
    savings_challenge = models.ForeignKey('SavingsChallenge', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'dashboard_transactions'
        verbose_name = 'Transaction Dashboard'
        verbose_name_plural = 'Transactions Dashboard'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount} FCFA"

class UserDashboardStats(models.Model):
    """Statistiques du dashboard utilisateur (cache)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    
    # Statistiques du portefeuille
    total_portfolio_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_invested_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    global_performance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Statistiques d'épargne
    current_month_savings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    savings_rank = models.IntegerField(default=0)
    total_savings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Métadonnées
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_dashboard_stats'
        verbose_name = 'Statistiques Dashboard'
        verbose_name_plural = 'Statistiques Dashboard'
    
    def __str__(self):
        return f"Stats - {self.user.username}"
    
    def refresh_stats(self):
        """Recalcule les statistiques"""
        from django.db.models import Sum
        from datetime import datetime
        
        # Calcul du portefeuille
        investments = UserInvestment.objects.filter(user=self.user, is_active=True)
        self.total_portfolio_value = investments.aggregate(
            total=Sum('current_value')
        )['total'] or 0
        
        self.total_invested_amount = investments.aggregate(
            total=Sum('invested_amount')
        )['total'] or 0
        
        # Performance globale
        if self.total_invested_amount > 0:
            self.global_performance_percentage = (
                (self.total_portfolio_value - self.total_invested_amount) / 
                self.total_invested_amount
            ) * 100
        
        # Épargne du mois actuel
        current_month = datetime.now().replace(day=1)
        self.current_month_savings = DashboardTransaction.objects.filter(
            user=self.user,
            transaction_type='SAVINGS',
            status='CONFIRMED',
            created_at__gte=current_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Rang d'épargne (simplifié)
        SavingsChallenge = get_savings_challenge_model()
        active_challenge = SavingsChallenge.objects.filter(status='ACTIVE').first()
        if active_challenge:
            user_progress = UserSavingsProgress.objects.filter(
                user=self.user, 
                challenge=active_challenge
            ).first()
            if user_progress:
                self.savings_rank = user_progress.rank
        
        self.save()
        
        # Log pour debug
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Stats refreshed for {self.user.email}: portfolio={self.total_portfolio_value}, invested={self.total_invested_amount}, performance={self.global_performance_percentage}%")
