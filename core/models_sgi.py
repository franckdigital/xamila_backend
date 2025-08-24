"""
Modèles pour la gestion des SGI (Sociétés de Gestion d'Investissement)
et des managers SGI dans la plateforme fintech Xamila
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

from .models import SGI as BaseSGI  # Import du modèle SGI de base

User = get_user_model()


class SGIExtended(BaseSGI):
    """
    Extension du modèle SGI de base avec fonctionnalités avancées
    pour la gestion institutionnelle et l'onboarding
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente de validation'),
        ('APPROVED', 'Approuvée'),
        ('REJECTED', 'Rejetée'),
        ('SUSPENDED', 'Suspendue'),
        ('ACTIVE', 'Active'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('EQUITY', 'Actions'),
        ('BONDS', 'Obligations'),
        ('MIXED', 'Mixte'),
        ('REAL_ESTATE', 'Immobilier'),
        ('COMMODITIES', 'Matières premières'),
        ('CRYPTO', 'Cryptomonnaies'),
        ('ESG', 'Investissement responsable'),
        ('PRIVATE_EQUITY', 'Capital investissement'),
        ('HEDGE_FUNDS', 'Fonds spéculatifs'),
    ]
    
    RISK_PROFILE_CHOICES = [
        ('CONSERVATIVE', 'Conservateur'),
        ('MODERATE', 'Modéré'),
        ('AGGRESSIVE', 'Agressif'),
        ('BALANCED', 'Équilibré'),
    ]
    
    # Informations réglementaires
    registration_number = models.CharField(max_length=50, unique=True, help_text="Numéro d'agrément AMF")
    
    # Statut avancé (étend le is_active de base)
    name = models.CharField(max_length=200, help_text="Nom de la SGI")
    legal_name = models.CharField(max_length=200, help_text="Raison sociale")
    description = models.TextField(help_text="Description de la SGI")
    
    # Contact
    email = models.EmailField(help_text="Email principal de la SGI")
    phone = models.CharField(max_length=20, help_text="Téléphone principal")
    website = models.URLField(blank=True, null=True, help_text="Site web")
    
    # Adresse
    address_line_1 = models.CharField(max_length=200, help_text="Adresse ligne 1")
    address_line_2 = models.CharField(max_length=200, blank=True, null=True, help_text="Adresse ligne 2")
    city = models.CharField(max_length=100, help_text="Ville")
    postal_code = models.CharField(max_length=20, help_text="Code postal")
    country = models.CharField(max_length=100, default="France", help_text="Pays")
    
    # Informations financières
    aum = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Actifs sous gestion (en euros)"
    )
    minimum_investment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Investissement minimum (en euros)"
    )
    management_fees = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Frais de gestion (en %)"
    )
    performance_fees = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        blank=True, 
        null=True,
        help_text="Frais de performance (en %)"
    )
    
    # Profil d'investissement
    specializations = models.JSONField(
        default=list,
        help_text="Spécialisations de la SGI (liste des SPECIALIZATION_CHOICES)"
    )
    risk_profile = models.CharField(
        max_length=20, 
        choices=RISK_PROFILE_CHOICES,
        help_text="Profil de risque principal"
    )
    target_return = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(-50), MaxValueValidator(100)],
        blank=True, 
        null=True,
        help_text="Rendement cible annuel (en %)"
    )
    
    # Critères de matching
    min_client_age = models.PositiveIntegerField(
        default=18, 
        validators=[MinValueValidator(18), MaxValueValidator(100)],
        help_text="Âge minimum des clients"
    )
    max_client_age = models.PositiveIntegerField(
        default=80, 
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        help_text="Âge maximum des clients"
    )
    min_monthly_income = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Revenu mensuel minimum requis (en euros)"
    )
    accepted_countries = models.JSONField(
        default=list,
        help_text="Pays acceptés pour les clients"
    )
    
    # Statut et validation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_active = models.BooleanField(default=True, help_text="SGI active sur la plateforme")
    is_featured = models.BooleanField(default=False, help_text="SGI mise en avant")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_at = models.DateTimeField(blank=True, null=True, help_text="Date de validation")
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='validated_sgis',
        help_text="Administrateur qui a validé la SGI"
    )
    
    # Documents et certifications
    amf_license_document = models.FileField(
        upload_to='sgi_documents/amf_licenses/', 
        blank=True, 
        null=True,
        help_text="Document d'agrément AMF"
    )
    insurance_document = models.FileField(
        upload_to='sgi_documents/insurance/', 
        blank=True, 
        null=True,
        help_text="Attestation d'assurance"
    )
    
    class Meta:
        db_table = 'sgi'
        verbose_name = 'SGI'
        verbose_name_plural = 'SGI'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"
    
    @property
    def is_validated(self):
        """Retourne True si la SGI est validée"""
        return self.status == 'APPROVED'
    
    @property
    def total_clients(self):
        """Nombre total de clients de la SGI"""
        return self.client_sgi_relationships.filter(status='ACTIVE').count()
    
    def get_specializations_display(self):
        """Retourne les spécialisations sous forme lisible"""
        spec_dict = dict(self.SPECIALIZATION_CHOICES)
        return [spec_dict.get(spec, spec) for spec in self.specializations]


class SGIManager(models.Model):
    """
    Modèle pour les managers/gestionnaires de SGI
    Un manager peut gérer une ou plusieurs SGI
    """
    
    ROLE_CHOICES = [
        ('MANAGER', 'Manager principal'),
        ('ASSISTANT', 'Assistant manager'),
        ('ANALYST', 'Analyste'),
        ('ADVISOR', 'Conseiller'),
    ]
    
    # Relation avec l'utilisateur
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='sgi_manager_profile'
    )
    
    # SGI gérées
    managed_sgis = models.ManyToManyField(
        SGI, 
        through='SGIManagerAssignment',
        related_name='managers'
    )
    
    # Informations professionnelles
    professional_title = models.CharField(max_length=100, help_text="Titre professionnel")
    license_number = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Numéro de licence professionnelle"
    )
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Années d'expérience"
    )
    
    # Spécialisations
    specializations = models.JSONField(
        default=list,
        help_text="Spécialisations du manager (liste des SPECIALIZATION_CHOICES)"
    )
    
    # Certifications
    certifications = models.JSONField(
        default=list,
        help_text="Certifications professionnelles"
    )
    
    # Contact professionnel
    professional_email = models.EmailField(help_text="Email professionnel")
    professional_phone = models.CharField(max_length=20, help_text="Téléphone professionnel")
    
    # Statut
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Manager vérifié par l'admin")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='verified_sgi_managers',
        help_text="Administrateur qui a vérifié le manager"
    )
    
    class Meta:
        db_table = 'sgi_manager'
        verbose_name = 'Manager SGI'
        verbose_name_plural = 'Managers SGI'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['license_number']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.professional_title}"
    
    @property
    def total_managed_sgis(self):
        """Nombre de SGI gérées"""
        return self.managed_sgis.count()


class SGIManagerAssignment(models.Model):
    """
    Modèle pour l'assignation des managers aux SGI
    Permet de gérer les rôles et permissions spécifiques
    """
    
    ROLE_CHOICES = [
        ('PRIMARY', 'Manager principal'),
        ('SECONDARY', 'Manager secondaire'),
        ('ANALYST', 'Analyste'),
        ('ADVISOR', 'Conseiller'),
    ]
    
    PERMISSION_CHOICES = [
        ('VIEW', 'Consultation'),
        ('EDIT', 'Modification'),
        ('MANAGE_CLIENTS', 'Gestion clients'),
        ('FINANCIAL_REPORTS', 'Rapports financiers'),
        ('ADMIN', 'Administration complète'),
    ]
    
    # Relations
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='manager_assignments')
    manager = models.ForeignKey(SGIManager, on_delete=models.CASCADE, related_name='sgi_assignments')
    
    # Rôle et permissions
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SECONDARY')
    permissions = models.JSONField(
        default=list,
        help_text="Permissions du manager pour cette SGI"
    )
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    # Métadonnées
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='sgi_assignments_created',
        help_text="Qui a créé cette assignation"
    )
    
    class Meta:
        db_table = 'sgi_manager_assignment'
        verbose_name = 'Assignation Manager SGI'
        verbose_name_plural = 'Assignations Managers SGI'
        unique_together = ['sgi', 'manager']
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['sgi', 'manager']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.manager.user.get_full_name()} -> {self.sgi.name} ({self.role})"


class ClientSGIRelationship(models.Model):
    """
    Modèle pour les relations entre clients et SGI
    Historique des matchings et des contrats
    """
    
    STATUS_CHOICES = [
        ('MATCHED', 'Matching effectué'),
        ('CONTACTED', 'Client contacté'),
        ('INTERESTED', 'Client intéressé'),
        ('CONTRACT_SENT', 'Contrat envoyé'),
        ('CONTRACT_SIGNED', 'Contrat signé'),
        ('ACTIVE', 'Relation active'),
        ('SUSPENDED', 'Suspendue'),
        ('TERMINATED', 'Terminée'),
        ('REJECTED', 'Rejetée'),
    ]
    
    SOURCE_CHOICES = [
        ('SMART_MATCHING', 'Matching intelligent'),
        ('MANUAL_SELECTION', 'Sélection manuelle'),
        ('REFERRAL', 'Recommandation'),
        ('DIRECT_CONTACT', 'Contact direct'),
    ]
    
    # Relations
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sgi_relationships',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='client_relationships')
    assigned_manager = models.ForeignKey(
        SGIManager, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='client_relationships'
    )
    
    # Informations du matching
    matching_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True, 
        null=True,
        help_text="Score de compatibilité (0-100%)"
    )
    matching_criteria = models.JSONField(
        default=dict,
        help_text="Critères utilisés pour le matching"
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='SMART_MATCHING')
    
    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='MATCHED')
    notes = models.TextField(blank=True, null=True, help_text="Notes sur la relation")
    
    # Informations contractuelles
    contract_sent_at = models.DateTimeField(blank=True, null=True)
    contract_signed_at = models.DateTimeField(blank=True, null=True)
    initial_investment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Investissement initial (en euros)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='created_sgi_relationships'
    )
    
    class Meta:
        db_table = 'client_sgi_relationship'
        verbose_name = 'Relation Client-SGI'
        verbose_name_plural = 'Relations Client-SGI'
        unique_together = ['client', 'sgi']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'sgi']),
            models.Index(fields=['status']),
            models.Index(fields=['source']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} -> {self.sgi.name} ({self.status})"
    
    @property
    def is_active_relationship(self):
        """Retourne True si la relation est active"""
        return self.status == 'ACTIVE'


class SGIPerformance(models.Model):
    """
    Modèle pour suivre les performances des SGI
    """
    
    PERIOD_CHOICES = [
        ('MONTHLY', 'Mensuel'),
        ('QUARTERLY', 'Trimestriel'),
        ('YEARLY', 'Annuel'),
    ]
    
    # Relations
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='performance_records')
    
    # Période
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField(help_text="Début de la période")
    period_end = models.DateField(help_text="Fin de la période")
    
    # Métriques de performance
    return_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        help_text="Taux de rendement (%)"
    )
    volatility = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        blank=True, 
        null=True,
        help_text="Volatilité (%)"
    )
    sharpe_ratio = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        blank=True, 
        null=True,
        help_text="Ratio de Sharpe"
    )
    max_drawdown = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        blank=True, 
        null=True,
        help_text="Drawdown maximum (%)"
    )
    
    # Métriques business
    new_clients = models.PositiveIntegerField(default=0, help_text="Nouveaux clients")
    total_clients = models.PositiveIntegerField(default=0, help_text="Total clients")
    aum_growth = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0,
        help_text="Croissance des AUM (%)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sgi_performance'
        verbose_name = 'Performance SGI'
        verbose_name_plural = 'Performances SGI'
        unique_together = ['sgi', 'period_type', 'period_start', 'period_end']
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['sgi', 'period_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.sgi.name} - {self.period_type} {self.period_start} to {self.period_end}"
