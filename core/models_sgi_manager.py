"""
Modèles spécialisés pour les SGI_MANAGER
Gestion avancée des Sociétés de Gestion d'Investissement
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class SGIManagerProfile(models.Model):
    """
    Profil étendu pour les managers SGI
    """
    
    PERMISSION_LEVELS = [
        ('READ_ONLY', 'Lecture seule'),
        ('STANDARD', 'Standard'),
        ('ADVANCED', 'Avancé'),
        ('FULL_ACCESS', 'Accès complet'),
    ]
    
    MANAGER_TYPES = [
        ('GENERAL_MANAGER', 'Directeur Général'),
        ('PORTFOLIO_MANAGER', 'Gestionnaire de Portefeuille'),
        ('SALES_MANAGER', 'Manager Commercial'),
        ('COMPLIANCE_MANAGER', 'Manager Conformité'),
        ('OPERATIONS_MANAGER', 'Manager Opérations'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='sgi_manager_profile'
    )
    sgi = models.ForeignKey(
        'SGI', 
        on_delete=models.CASCADE, 
        related_name='managers'
    )
    
    # Informations professionnelles
    manager_type = models.CharField(
        max_length=30, 
        choices=MANAGER_TYPES,
        default='PORTFOLIO_MANAGER',
        verbose_name="Type de manager"
    )
    employee_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="ID employé"
    )
    department = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Département"
    )
    hire_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name="Date d'embauche"
    )
    
    # Permissions et accès
    permission_level = models.CharField(
        max_length=20, 
        choices=PERMISSION_LEVELS,
        default='STANDARD',
        verbose_name="Niveau de permission"
    )
    can_approve_contracts = models.BooleanField(
        default=False,
        verbose_name="Peut approuver les contrats"
    )
    can_manage_clients = models.BooleanField(
        default=True,
        verbose_name="Peut gérer les clients"
    )
    can_view_financials = models.BooleanField(
        default=False,
        verbose_name="Peut voir les données financières"
    )
    can_generate_reports = models.BooleanField(
        default=True,
        verbose_name="Peut générer des rapports"
    )
    
    # Limites opérationnelles
    max_contract_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Montant max de contrat approuvable (FCFA)"
    )
    max_daily_approvals = models.PositiveIntegerField(
        default=10,
        verbose_name="Nombre max d'approbations par jour"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Profil Manager SGI"
        verbose_name_plural = "Profils Managers SGI"
        unique_together = ['user', 'sgi']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sgi.name} ({self.manager_type})"
    
    def can_approve_amount(self, amount):
        """Vérifie si le manager peut approuver un montant donné"""
        if not self.can_approve_contracts:
            return False
        if self.max_contract_amount and amount > self.max_contract_amount:
            return False
        return True
    
    def get_daily_approvals_count(self):
        """Compte les approbations du jour"""
        today = timezone.now().date()
        from .models import Contract
        return Contract.objects.filter(
            approved_by=self.user,
            approved_at__date=today
        ).count()
    
    def can_approve_today(self):
        """Vérifie si le manager peut encore approuver aujourd'hui"""
        return self.get_daily_approvals_count() < self.max_daily_approvals


class SGIPerformanceMetrics(models.Model):
    """
    Métriques de performance d'une SGI
    """
    
    METRIC_PERIODS = [
        ('DAILY', 'Quotidien'),
        ('WEEKLY', 'Hebdomadaire'),
        ('MONTHLY', 'Mensuel'),
        ('QUARTERLY', 'Trimestriel'),
        ('YEARLY', 'Annuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sgi = models.ForeignKey(
        'SGI', 
        on_delete=models.CASCADE, 
        related_name='performance_metrics'
    )
    
    # Période de mesure
    period_type = models.CharField(
        max_length=20, 
        choices=METRIC_PERIODS,
        verbose_name="Type de période"
    )
    period_start = models.DateTimeField(verbose_name="Début de période")
    period_end = models.DateTimeField(verbose_name="Fin de période")
    
    # Métriques clients
    new_clients = models.PositiveIntegerField(
        default=0,
        verbose_name="Nouveaux clients"
    )
    active_clients = models.PositiveIntegerField(
        default=0,
        verbose_name="Clients actifs"
    )
    churned_clients = models.PositiveIntegerField(
        default=0,
        verbose_name="Clients perdus"
    )
    
    # Métriques financières
    total_investments = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total investissements (FCFA)"
    )
    average_investment = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Investissement moyen (FCFA)"
    )
    total_fees_collected = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total frais collectés (FCFA)"
    )
    
    # Métriques de performance
    portfolio_return = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('-100')), MaxValueValidator(Decimal('1000'))],
        verbose_name="Rendement portefeuille (%)"
    )
    benchmark_return = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('-100')), MaxValueValidator(Decimal('1000'))],
        verbose_name="Rendement benchmark (%)"
    )
    
    # Métriques opérationnelles
    contracts_signed = models.PositiveIntegerField(
        default=0,
        verbose_name="Contrats signés"
    )
    contracts_pending = models.PositiveIntegerField(
        default=0,
        verbose_name="Contrats en attente"
    )
    contracts_rejected = models.PositiveIntegerField(
        default=0,
        verbose_name="Contrats rejetés"
    )
    
    # Satisfaction client
    client_satisfaction_score = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))],
        verbose_name="Score satisfaction client (/10)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Métrique de Performance SGI"
        verbose_name_plural = "Métriques de Performance SGI"
        unique_together = ['sgi', 'period_type', 'period_start']
        ordering = ['-period_start']
        
    def __str__(self):
        return f"{self.sgi.name} - {self.period_type} ({self.period_start.strftime('%Y-%m-%d')})"
    
    @property
    def client_retention_rate(self):
        """Calcule le taux de rétention client"""
        if self.active_clients + self.churned_clients == 0:
            return 0
        return (self.active_clients / (self.active_clients + self.churned_clients)) * 100
    
    @property
    def contract_success_rate(self):
        """Calcule le taux de succès des contrats"""
        total_contracts = self.contracts_signed + self.contracts_rejected
        if total_contracts == 0:
            return 0
        return (self.contracts_signed / total_contracts) * 100
    
    @property
    def alpha_performance(self):
        """Calcule l'alpha (performance vs benchmark)"""
        return self.portfolio_return - self.benchmark_return


class SGIClientRelationship(models.Model):
    """
    Relation entre un manager SGI et un client
    """
    
    RELATIONSHIP_TYPES = [
        ('PRIMARY', 'Manager principal'),
        ('SECONDARY', 'Manager secondaire'),
        ('ADVISOR', 'Conseiller'),
        ('SUPPORT', 'Support'),
    ]
    
    RELATIONSHIP_STATUS = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('SUSPENDED', 'Suspendu'),
        ('TERMINATED', 'Terminé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manager = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='managed_clients'
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sgi_managers'
    )
    sgi = models.ForeignKey(
        'SGI', 
        on_delete=models.CASCADE, 
        related_name='client_relationships'
    )
    
    relationship_type = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_TYPES,
        default='PRIMARY',
        verbose_name="Type de relation"
    )
    status = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_STATUS,
        default='ACTIVE',
        verbose_name="Statut"
    )
    
    # Dates importantes
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de début"
    )
    end_date = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Date de fin"
    )
    last_contact = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Dernier contact"
    )
    
    # Notes et commentaires
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Relation Client SGI"
        verbose_name_plural = "Relations Clients SGI"
        unique_together = ['manager', 'client', 'sgi']
        
    def __str__(self):
        return f"{self.manager.get_full_name()} -> {self.client.get_full_name()} ({self.sgi.name})"
    
    def is_active(self):
        """Vérifie si la relation est active"""
        return self.status == 'ACTIVE' and (not self.end_date or self.end_date > timezone.now())
    
    def days_since_last_contact(self):
        """Calcule le nombre de jours depuis le dernier contact"""
        if not self.last_contact:
            return None
        return (timezone.now() - self.last_contact).days


class SGIAlert(models.Model):
    """
    Alertes et notifications pour les managers SGI
    """
    
    ALERT_TYPES = [
        ('CONTRACT_PENDING', 'Contrat en attente'),
        ('CLIENT_INACTIVE', 'Client inactif'),
        ('PERFORMANCE_LOW', 'Performance faible'),
        ('COMPLIANCE_ISSUE', 'Problème de conformité'),
        ('SYSTEM_UPDATE', 'Mise à jour système'),
        ('MARKET_NEWS', 'Actualité marché'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
        ('CRITICAL', 'Critique'),
    ]
    
    ALERT_STATUS = [
        ('UNREAD', 'Non lu'),
        ('READ', 'Lu'),
        ('ACKNOWLEDGED', 'Accusé réception'),
        ('RESOLVED', 'Résolu'),
        ('DISMISSED', 'Ignoré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manager = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sgi_alerts'
    )
    sgi = models.ForeignKey(
        'SGI', 
        on_delete=models.CASCADE, 
        related_name='alerts'
    )
    
    alert_type = models.CharField(
        max_length=30, 
        choices=ALERT_TYPES,
        verbose_name="Type d'alerte"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_LEVELS,
        default='MEDIUM',
        verbose_name="Priorité"
    )
    status = models.CharField(
        max_length=20, 
        choices=ALERT_STATUS,
        default='UNREAD',
        verbose_name="Statut"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )
    message = models.TextField(verbose_name="Message")
    action_required = models.BooleanField(
        default=False,
        verbose_name="Action requise"
    )
    action_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name="URL d'action"
    )
    
    # Métadonnées
    related_object_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Type d'objet lié"
    )
    related_object_id = models.UUIDField(
        blank=True, 
        null=True,
        verbose_name="ID objet lié"
    )
    
    expires_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Expire le"
    )
    read_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Lu le"
    )
    acknowledged_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Accusé réception le"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Alerte SGI"
        verbose_name_plural = "Alertes SGI"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.manager.get_full_name()} ({self.priority})"
    
    def mark_as_read(self):
        """Marque l'alerte comme lue"""
        if self.status == 'UNREAD':
            self.status = 'READ'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])
    
    def acknowledge(self):
        """Accuse réception de l'alerte"""
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = timezone.now()
        self.save(update_fields=['status', 'acknowledged_at'])
    
    def is_expired(self):
        """Vérifie si l'alerte a expiré"""
        return self.expires_at and self.expires_at < timezone.now()
