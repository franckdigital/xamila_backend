from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
import uuid
import random
import string
from datetime import timedelta

# Les imports des modèles spécialisés seront ajoutés après la définition du User


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer un utilisateur normal"""
        if not email:
            raise ValueError('L\'email est requis')
        
        email = self.normalize_email(email)
        
        # Générer un username unique si pas fourni
        if 'username' not in extra_fields:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter:04d}"
                counter += 1
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Créer un superutilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modèle utilisateur étendu pour XAMILA
    """
    
    # Rôles utilisateur complets basés sur les fonctionnalités XAMILA
    ROLE_CHOICES = [
        ('CUSTOMER', 'Client/Épargnant'),
        ('STUDENT', 'Étudiant/Apprenant'),
        ('SGI_MANAGER', 'Manager SGI'),
        ('INSTRUCTOR', 'Instructeur/Formateur'),
        ('SUPPORT', 'Support Client'),
        ('ADMIN', 'Administrateur'),
    ]
    
    # Informations personnelles étendues
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Redéfinir email pour le rendre unique (requis pour USERNAME_FIELD)
    email = models.EmailField(
        unique=True,
        verbose_name='Email address',
        help_text='Adresse email unique pour l\'authentification'
    )
    
    phone = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Numéro de téléphone invalide')]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    
    # Pays
    country_of_residence = models.CharField(max_length=100, blank=True, null=True)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    
    # Statut de vérification
    is_verified = models.BooleanField(default=False, verbose_name="Compte vérifié")
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Correction des conflits reverse accessor
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='xamila_users',
        related_query_name='xamila_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='xamila_users',
        related_query_name='xamila_user',
    )
    
    
    # Utiliser le manager personnalisé
    objects = UserManager()
    
    # Configuration pour utiliser l'email comme identifiant principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class OTP(models.Model):
    """
    Codes OTP pour vérification (inscription, réinitialisation mot de passe)
    """
    
    OTP_TYPES = [
        ('REGISTRATION', 'Inscription'),
        ('PASSWORD_RESET', 'Réinitialisation mot de passe'),
        ('EMAIL_VERIFICATION', 'Vérification email'),
        ('PHONE_VERIFICATION', 'Vérification téléphone'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6, verbose_name="Code OTP")
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    
    # Statut et validité
    is_used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', 'is_used']),
            models.Index(fields=['code', 'expires_at']),
        ]
    
    def __str__(self):
        return f"OTP {self.code} - {self.user.username} ({self.get_otp_type_display()})"
    
    @classmethod
    def generate_code(cls):
        """Génère un code OTP à 6 chiffres"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """Vérifie si le code OTP est encore valide"""
        return not self.is_used and not self.is_expired and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marque le code comme utilisé"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)


class RefreshToken(models.Model):
    """
    Tokens de rafraîchissement JWT
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)  # Changé de TextField à CharField pour MySQL
    
    # Validité
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Token de rafraîchissement"
        verbose_name_plural = "Tokens de rafraîchissement"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_revoked']),
        ]
    
    def __str__(self):
        return f"RefreshToken - {self.user.username} ({self.created_at})"
    
    def is_valid(self):
        """Vérifie si le token est encore valide"""
        return not self.is_revoked and timezone.now() < self.expires_at
    
    def revoke(self):
        """Révoque le token"""
        self.is_revoked = True
        self.save()


class SGI(models.Model):
    """
    Modèle de base pour les Sociétés de Gestion d'Investissement (SGI)
    Contient uniquement les informations essentielles utilisées par tous les rôles
    """
    
    # Identifiants
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom de la SGI")
    description = models.TextField(verbose_name="Description")
    logo = models.ImageField(upload_to='sgi_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(verbose_name="Email principal")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(verbose_name="Adresse")
    
    # Manager principal
    manager_name = models.CharField(max_length=100, verbose_name="Nom du manager")
    manager_email = models.EmailField(verbose_name="Email du manager")
    manager_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Objectifs et critères d'investissement (constantes partagées)
    INVESTMENT_OBJECTIVES = [
        ('GROWTH', 'Croissance'),
        ('INCOME', 'Revenus'),
        ('BALANCED', 'Équilibré'),
        ('CONSERVATIVE', 'Conservateur'),
        ('AGGRESSIVE', 'Agressif'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Faible'),
        ('MODERATE', 'Modéré'),
        ('HIGH', 'Élevé'),
    ]
    
    INVESTMENT_HORIZONS = [
        ('SHORT', 'Court terme (< 2 ans)'),
        ('MEDIUM', 'Moyen terme (2-5 ans)'),
        ('LONG', 'Long terme (> 5 ans)'),
    ]
    
    # Montants d'investissement
    min_investment_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant minimum d'investissement"
    )
    
    max_investment_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name="Montant maximum d'investissement (optionnel)"
    )
    
    # Performance et frais de base
    historical_performance = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('-100')), MaxValueValidator(Decimal('1000'))],
        default=Decimal('0.00'),
        verbose_name="Performance historique (%)"
    )
    
    management_fees = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))],
        default=Decimal('2.00'),
        verbose_name="Frais de gestion (%)"
    )
    
    entry_fees = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))],
        default=Decimal('0.00'),
        verbose_name="Frais d'entrée (%)"
    )
    
    # Statut de base
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifiée")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SGI"
        verbose_name_plural = "SGI"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ClientInvestmentProfile(models.Model):
    """
    Profil d'investissement d'un client
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investment_profile')
    
    # Informations personnelles
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    profession = models.CharField(max_length=100, verbose_name="Profession")
    monthly_income = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="Revenus mensuels (FCFA)"
    )
    
    # Préférences d'investissement
    investment_objective = models.CharField(
        max_length=20, choices=SGI.INVESTMENT_OBJECTIVES,
        verbose_name="Objectif d'investissement"
    )
    
    risk_tolerance = models.CharField(
        max_length=20, choices=SGI.RISK_LEVELS,
        verbose_name="Tolérance au risque"
    )
    
    investment_horizon = models.CharField(
        max_length=20, choices=SGI.INVESTMENT_HORIZONS,
        verbose_name="Horizon d'investissement"
    )
    
    investment_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('10000'))],
        verbose_name="Montant à investir (FCFA)"
    )
    
    # Expérience d'investissement
    EXPERIENCE_LEVELS = [
        ('BEGINNER', 'Débutant'),
        ('INTERMEDIATE', 'Intermédiaire'),
        ('ADVANCED', 'Avancé'),
        ('EXPERT', 'Expert'),
    ]
    
    investment_experience = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVELS,
        verbose_name="Expérience d'investissement"
    )
    
    # Préférences additionnelles
    preferred_sectors = models.JSONField(
        default=list, blank=True,
        verbose_name="Secteurs préférés",
        help_text="Liste des secteurs d'activité préférés"
    )
    
    exclude_sectors = models.JSONField(
        default=list, blank=True,
        verbose_name="Secteurs à exclure",
        help_text="Liste des secteurs à éviter"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(default=False, verbose_name="Profil complet")
    
    class Meta:
        verbose_name = "Profil d'investissement client"
        verbose_name_plural = "Profils d'investissement clients"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profil de {self.full_name}"
    
    @property
    def age(self):
        """Calcule l'âge du client"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class SGIMatchingRequest(models.Model):
    """
    Demande de matching entre un client et des SGI
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_profile = models.ForeignKey(
        ClientInvestmentProfile, on_delete=models.CASCADE,
        related_name='matching_requests'
    )
    
    # Résultats du matching
    matched_sgis = models.JSONField(
        default=list,
        verbose_name="SGI matchées",
        help_text="Liste des SGI avec leurs scores de compatibilité"
    )
    
    total_matches = models.PositiveIntegerField(default=0, verbose_name="Nombre de matches")
    
    # Statut de la demande
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En cours de traitement'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échec'),
    ]
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='PENDING', verbose_name="Statut"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Demande de matching SGI"
        verbose_name_plural = "Demandes de matching SGI"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Matching pour {self.client_profile.full_name} - {self.status}"


class ClientSGIInteraction(models.Model):
    """
    Interaction entre un client et une SGI (sélection, contact, etc.)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_profile = models.ForeignKey(
        ClientInvestmentProfile, on_delete=models.CASCADE,
        related_name='sgi_interactions'
    )
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='client_interactions')
    matching_request = models.ForeignKey(
        SGIMatchingRequest, on_delete=models.CASCADE, blank=True, null=True,
        related_name='interactions'
    )
    
    # Type d'interaction
    INTERACTION_TYPES = [
        ('VIEW', 'Consultation'),
        ('CONTACT', 'Prise de contact'),
        ('SELECTION', 'Sélection'),
        ('MEETING', 'Rendez-vous'),
        ('CONTRACT', 'Signature contrat'),
    ]
    
    interaction_type = models.CharField(
        max_length=20, choices=INTERACTION_TYPES,
        verbose_name="Type d'interaction"
    )
    
    # Score de matching au moment de l'interaction
    matching_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de compatibilité"
    )
    
    # Détails de l'interaction
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Statut du suivi
    STATUS_CHOICES = [
        ('INITIATED', 'Initié'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='INITIATED', verbose_name="Statut"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interaction Client-SGI"
        verbose_name_plural = "Interactions Client-SGI"
        ordering = ['-created_at']
        unique_together = ['client_profile', 'sgi', 'interaction_type', 'created_at']
    
    def __str__(self):
        return f"{self.client_profile.full_name} - {self.sgi.name} ({self.interaction_type})"


class EmailNotification(models.Model):
    """
    Notifications email envoyées dans le système
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Destinataire et expéditeur
    to_email = models.EmailField(verbose_name="Email destinataire")
    from_email = models.EmailField(verbose_name="Email expéditeur")
    
    # Contenu de l'email
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    html_message = models.TextField(blank=True, verbose_name="Message HTML")
    
    # Type de notification
    NOTIFICATION_TYPES = [
        ('SGI_MANAGER', 'Notification manager SGI'),
        ('CLIENT_CONFIRMATION', 'Confirmation client'),
        ('XAMILA_NOTIFICATION', 'Notification équipe Xamila'),
        ('SYSTEM', 'Notification système'),
    ]
    
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPES,
        verbose_name="Type de notification"
    )
    
    # Références
    client_interaction = models.ForeignKey(
        ClientSGIInteraction, on_delete=models.CASCADE, blank=True, null=True,
        related_name='email_notifications'
    )
    
    # Statut d'envoi
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('SENT', 'Envoyé'),
        ('FAILED', 'Échec'),
        ('BOUNCED', 'Rejeté'),
    ]
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='PENDING', verbose_name="Statut d'envoi"
    )
    
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Notification email"
        verbose_name_plural = "Notifications email"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.to_email} ({self.status})"


class AdminDashboardEntry(models.Model):
    """
    Entrées du dashboard admin pour le suivi des interactions SGI
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Référence à l'interaction
    client_interaction = models.OneToOneField(
        ClientSGIInteraction, on_delete=models.CASCADE,
        related_name='dashboard_entry'
    )
    
    # Priorité basée sur le montant d'investissement
    PRIORITY_LEVELS = [
        ('LOW', 'Faible (< 1M FCFA)'),
        ('MEDIUM', 'Moyenne (1M - 10M FCFA)'),
        ('HIGH', 'Élevée (10M - 50M FCFA)'),
        ('CRITICAL', 'Critique (> 50M FCFA)'),
    ]
    
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS,
        verbose_name="Niveau de priorité"
    )
    
    # Statut de suivi admin
    FOLLOW_UP_STATUS = [
        ('NEW', 'Nouveau'),
        ('CONTACTED', 'Contacté'),
        ('IN_NEGOTIATION', 'En négociation'),
        ('CLOSED_WON', 'Conclu (gagné)'),
        ('CLOSED_LOST', 'Conclu (perdu)'),
    ]
    
    follow_up_status = models.CharField(
        max_length=20, choices=FOLLOW_UP_STATUS,
        default='NEW', verbose_name="Statut de suivi"
    )
    
    # Notes administratives
    admin_notes = models.TextField(blank=True, verbose_name="Notes administratives")
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='assigned_dashboard_entries',
        verbose_name="Assigné à"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Entrée dashboard admin"
        verbose_name_plural = "Entrées dashboard admin"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"Dashboard: {self.client_interaction} - {self.priority}"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement la priorité basée sur le montant d'investissement"""
        if not self.priority:
            amount = self.client_interaction.client_profile.investment_amount
            if amount >= 50000000:  # 50M FCFA
                self.priority = 'CRITICAL'
            elif amount >= 10000000:  # 10M FCFA
                self.priority = 'HIGH'
            elif amount >= 1000000:  # 1M FCFA
                self.priority = 'MEDIUM'
            else:
                self.priority = 'LOW'
        
        super().save(*args, **kwargs)


class Contract(models.Model):
    """
    Contrats d'investissement entre clients et SGI
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('CANCELLED', 'Annulé'),
    ]
    
    FUNDING_SOURCES = [
        ('VISA', 'Carte Visa'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Virement bancaire'),
        ('CASH', 'Espèces'),
        ('OTHER', 'Autre'),
    ]
    
    # Identifiants
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_number = models.CharField(
        max_length=50, unique=True, blank=True,
        verbose_name="Numéro de contrat"
    )
    
    # Relations
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='contracts',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='contracts')
    
    # Informations du contrat
    investment_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('1000'))],
        verbose_name="Montant d'investissement (FCFA)"
    )
    
    funding_source = models.CharField(
        max_length=20, choices=FUNDING_SOURCES,
        verbose_name="Source de financement"
    )
    
    # Informations bancaires (si applicable)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Statut et workflow
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='PENDING', verbose_name="Statut"
    )
    
    # Notes et commentaires
    customer_notes = models.TextField(blank=True, verbose_name="Notes du client")
    manager_notes = models.TextField(blank=True, verbose_name="Notes du manager")
    rejection_reason = models.TextField(blank=True, verbose_name="Raison du rejet")
    
    # Dates importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    
    # Traçabilité
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='approved_contracts',
        limit_choices_to={'role__in': ['SGI_MANAGER', 'ADMIN']}
    )
    
    class Meta:
        verbose_name = "Contrat d'investissement"
        verbose_name_plural = "Contrats d'investissement"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['sgi', 'status']),
            models.Index(fields=['contract_number']),
        ]
    
    def __str__(self):
        return f"{self.contract_number} - {self.customer.full_name} → {self.sgi.name}"
    
    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()
        super().save(*args, **kwargs)
    
    def generate_contract_number(self):
        """Génère un numéro de contrat unique au format XAMILA-YYYYMMDD-XXXX"""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        # Compter les contrats du jour
        daily_count = Contract.objects.filter(
            created_at__date=today
        ).count() + 1
        
        return f"XAMILA-{date_str}-{daily_count:04d}"
    
    def can_be_modified(self):
        """Vérifie si le contrat peut être modifié"""
        return self.status == 'PENDING'
    
    def approve(self, approved_by_user):
        """Approuve le contrat"""
        if self.status == 'PENDING':
            self.status = 'APPROVED'
            self.approved_by = approved_by_user
            self.approved_at = timezone.now()
            self.save()
    
    def reject(self, rejected_by_user, reason=""):
        """Rejette le contrat"""
        if self.status == 'PENDING':
            self.status = 'REJECTED'
            self.approved_by = rejected_by_user  # Pour traçabilité
            self.rejected_at = timezone.now()
            self.rejection_reason = reason
            self.save()


class QuizQuestion(models.Model):
    """
    Questions de quiz liées aux vidéos d'apprentissage
    """
    
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Choix multiple'),
        ('TRUE_FALSE', 'Vrai/Faux'),
        ('SINGLE_CHOICE', 'Choix unique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contenu de la question
    video_id = models.CharField(
        max_length=100, db_index=True,
        verbose_name="ID de la vidéo associée"
    )
    question_text = models.TextField(verbose_name="Texte de la question")
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES,
        default='MULTIPLE_CHOICE'
    )
    
    # Options de réponse (JSON)
    options = models.JSONField(
        default=list,
        verbose_name="Options de réponse",
        help_text="Liste des options possibles"
    )
    
    # Réponse correcte
    correct_answer = models.JSONField(
        verbose_name="Réponse(s) correcte(s)",
        help_text="Index ou liste des bonnes réponses"
    )
    
    # Configuration
    order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )
    is_active = models.BooleanField(default=True, verbose_name="Question active")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_questions',
        limit_choices_to={'role__in': ['ADMIN', 'INSTRUCTOR']}
    )
    
    class Meta:
        verbose_name = "Question de quiz"
        verbose_name_plural = "Questions de quiz"
        ordering = ['video_id', 'order']
        indexes = [
            models.Index(fields=['video_id', 'is_active']),
            models.Index(fields=['video_id', 'order']),
        ]
    
    def __str__(self):
        return f"Question {self.video_id} - {self.question_text[:50]}..."


class QuizSubmission(models.Model):
    """
    Soumissions de quiz par les utilisateurs
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    video_id = models.CharField(max_length=100, db_index=True)
    
    # Réponses et résultats
    answers = models.JSONField(
        default=dict,
        verbose_name="Réponses utilisateur",
        help_text="Dictionnaire question_id: réponse"
    )
    
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score (%)"
    )
    
    total_questions = models.PositiveIntegerField(verbose_name="Nombre total de questions")
    correct_answers = models.PositiveIntegerField(verbose_name="Réponses correctes")
    
    # Temps
    time_spent = models.DurationField(
        blank=True, null=True,
        verbose_name="Temps passé"
    )
    
    # Métadonnées
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Soumission de quiz"
        verbose_name_plural = "Soumissions de quiz"
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'video_id']),
            models.Index(fields=['video_id', 'score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Video {self.video_id} - {self.score}%"


class Stock(models.Model):
    """
    Données de simulation de stocks/actions
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    symbol = models.CharField(
        max_length=10, unique=True, db_index=True,
        verbose_name="Symbole de l'action"
    )
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    
    # Prix et variations
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix actuel"
    )
    
    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix précédent"
    )
    
    # Calculs automatiques
    price_change = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Variation de prix"
    )
    
    price_change_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="Variation (%)"
    )
    
    # Volume et capitalisation
    volume = models.BigIntegerField(default=0, verbose_name="Volume d'échanges")
    market_cap = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True,
        verbose_name="Capitalisation boursière"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Action active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Action/Stock"
        verbose_name_plural = "Actions/Stocks"
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol', 'is_active']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"{self.symbol} - {self.company_name} ({self.current_price})"
    
    def save(self, *args, **kwargs):
        # Calculer automatiquement les variations
        if self.current_price and self.previous_price:
            self.price_change = self.current_price - self.previous_price
            if self.previous_price > 0:
                self.price_change_percent = (
                    (self.price_change / self.previous_price) * 100
                )
        super().save(*args, **kwargs)
    
    def simulate_price_change(self, max_change_percent=5.0):
        """Simule une variation de prix aléatoire"""
        self.previous_price = self.current_price
        
        # Variation aléatoire entre -max_change_percent et +max_change_percent
        change_percent = random.uniform(-max_change_percent, max_change_percent)
        change_amount = self.current_price * Decimal(change_percent / 100)
        
        self.current_price = max(
            Decimal('0.01'),  # Prix minimum
            self.current_price + change_amount
        )
        
        # Volume aléatoire
        self.volume = random.randint(1000, 100000)
        
        self.save()


# Import des modèles de blog
from .models_blog import *

# Import des modèles de challenge épargne
from .models_savings_challenge import *
