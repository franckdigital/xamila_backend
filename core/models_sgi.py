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
        BaseSGI, 
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
    sgi = models.ForeignKey(BaseSGI, on_delete=models.CASCADE, related_name='manager_assignments')
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
    sgi = models.ForeignKey(BaseSGI, on_delete=models.CASCADE, related_name='client_relationships')
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
    sgi = models.ForeignKey(BaseSGI, on_delete=models.CASCADE, related_name='performance_records')
    
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


class SGIAccountTerms(models.Model):
    """
    Conditions et informations d'ouverture de compte titre pour une SGI
    Utilisé par le comparateur et l'affichage détaillé
    """

    PAYMENT_METHODS = [
        ("BANK_TRANSFER", "Virement bancaire"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("VISA", "Carte Visa"),
        ("CASH", "Espèces"),
        ("CHECK", "Chèque"),
    ]

    REDEMPTION_METHODS = [
        ("BANK_TRANSFER", "Rachat par virement"),
        ("MOBILE_MONEY", "Rachat par mobile money"),
        ("CHECK", "Rachat par chèque"),
        ("VISA", "Rachat Visa"),
    ]

    sgi = models.OneToOneField(BaseSGI, on_delete=models.CASCADE, related_name="account_terms")

    # Localisation et identité
    country = models.CharField(max_length=100, verbose_name="Pays")
    headquarters_address = models.CharField(max_length=255, verbose_name="Adresse du siège")
    director_name = models.CharField(max_length=150, verbose_name="Nom du dirigeant")
    profile = models.TextField(verbose_name="Présentation/Profil de la SGI")

    # Montant minimum et frais d'ouverture
    has_minimum_amount = models.BooleanField(default=False)
    minimum_amount_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    has_opening_fees = models.BooleanField(default=False)
    opening_fees_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    # Modalités d'ouverture
    is_digital_opening = models.BooleanField(default=True, help_text="Ouverture 100% à distance")

    # Méthodes d'alimentation/dépôt
    deposit_methods = models.JSONField(default=list, help_text="Liste parmi PAYMENT_METHODS")

    # Filiale bancaire
    is_bank_subsidiary = models.BooleanField(default=False)
    parent_bank_name = models.CharField(max_length=150, blank=True, null=True)

    # Frais de garde et tenue de compte
    custody_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Frais de garde (FCFA ou %)")
    account_maintenance_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Frais de tenue de compte (FCFA ou %)")

    # Frais de courtage
    brokerage_fees_transactions_ordinary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brokerage_fees_files = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brokerage_fees_transactions = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Frais de transfert
    transfer_account_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transfer_securities_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Frais de nantissement
    pledge_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Méthodes de rachat
    redemption_methods = models.JSONField(default=list, help_text="Liste parmi REDEMPTION_METHODS")

    # Banques compatibles (si avantage client)
    preferred_customer_banks = models.JSONField(default=list, help_text="Noms de banques partenaires/compatibles")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conditions d'ouverture de compte SGI"
        verbose_name_plural = "Conditions d'ouverture de compte SGI"

    def __str__(self):
        return f"Terms - {self.sgi.name}"


class SGIRating(models.Model):
    """
    Notation de la réactivité/qualité de service d'une SGI par les clients
    """

    sgi = models.ForeignKey(BaseSGI, on_delete=models.CASCADE, related_name="ratings")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sgi_ratings", limit_choices_to={"role": "CUSTOMER"})
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["sgi", "customer"]
        indexes = [
            models.Index(fields=["sgi"]),
            models.Index(fields=["customer"]),
        ]

    def __str__(self):
        return f"Rating {self.score}/5 - {self.sgi.name} by {self.customer.get_full_name()}"


class AccountOpeningRequest(models.Model):
    """
    Demande de mise en relation / ouverture de compte titre
    Contient les champs du formulaire et les pièces KYC
    """

    FUNDING_CHOICES = [
        ("VISA", "Par Carte Visa"),
        ("MOBILE_MONEY", "Par Mobile Money"),
        ("BANK_TRANSFER", "Par Virement Bancaire"),
        ("INTERMEDIARY", "Par un intermédiaire/mandataire"),
        ("WU_MG_RIA", "Par WU, Money Gram, Ria"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account_opening_requests", limit_choices_to={"role": "CUSTOMER"})
    sgi = models.ForeignKey(BaseSGI, on_delete=models.SET_NULL, blank=True, null=True, related_name="account_opening_requests")

    # Coordonnées
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    is_phone_linked_to_kyc_mobile_money = models.BooleanField(default=False)
    alternate_kyc_mobile_money_phone = models.CharField(max_length=30, blank=True, null=True)

    # Pays
    country_of_residence = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    # Banque du client
    customer_banks_current_account = models.JSONField(default=list, help_text="Liste des banques avec compte courant")

    # Préférences d'ouverture
    wants_digital_opening = models.BooleanField(default=True)
    wants_in_person_opening = models.BooleanField(default=False)
    available_minimum_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    wants_100_percent_digital_sgi = models.BooleanField(default=False)

    # Méthodes d'alimentation
    funding_by_visa = models.BooleanField(default=False)
    funding_by_mobile_money = models.BooleanField(default=False)
    funding_by_bank_transfer = models.BooleanField(default=False)
    funding_by_intermediary = models.BooleanField(default=False)
    funding_by_wu_mg_ria = models.BooleanField(default=False)
    wants_xamila_as_intermediary = models.BooleanField(default=False)

    # Préférences coûts/qualité
    prefer_service_quality_over_fees = models.BooleanField(default=True)

    # LAB - Sources de revenus
    sources_of_income = models.TextField()

    # Profil d'investisseur
    INVESTOR_PROFILE_CHOICES = [
        ("PRUDENT", "Prudent"),
        ("AUDACIOUS", "Audacieux"),
        ("MODERATE", "Modéré"),
    ]
    investor_profile = models.CharField(max_length=20, choices=INVESTOR_PROFILE_CHOICES)

    # KYC (+IA)
    holder_info = models.TextField(blank=True, help_text="Infos sur le titulaire du compte")
    photo = models.ImageField(upload_to="kyc/account_opening/photos/", blank=True, null=True)
    id_card_scan = models.FileField(upload_to="kyc/account_opening/id_scans/", blank=True, null=True)

    # Xamila+
    wants_xamila_plus = models.BooleanField(default=False)
    authorize_xamila_to_receive_account_info = models.BooleanField(default=False)

    # Métadonnées
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande d'ouverture de compte titre"
        verbose_name_plural = "Demandes d'ouverture de compte titre"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["sgi"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"AccountOpeningRequest {self.id} - {self.full_name}"
