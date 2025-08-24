"""
Modèles KYC (Know Your Customer) pour XAMILA
Gestion complète de l'identification et vérification des clients
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
import os

User = get_user_model()


def kyc_document_upload_path(instance, filename):
    """Génère le chemin d'upload pour les documents KYC"""
    user_id = instance.kyc_profile.user.id
    document_type = instance.document_type.lower()
    ext = filename.split('.')[-1]
    return f'kyc_documents/{user_id}/{document_type}/{uuid.uuid4()}.{ext}'


class KYCProfile(models.Model):
    """
    Profil KYC d'un utilisateur CUSTOMER
    """
    
    KYC_STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('UNDER_REVIEW', 'En cours de vérification'),
        ('APPROVED', 'Validé'),
        ('REJECTED', 'Rejeté'),
        ('EXPIRED', 'Expiré'),
        ('SUSPENDED', 'Suspendu'),
    ]
    
    DOCUMENT_VERIFICATION_STATUS = [
        ('NOT_SUBMITTED', 'Non soumis'),
        ('SUBMITTED', 'Soumis'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
        ('VERY_HIGH', 'Très élevé'),
    ]
    
    # Relation avec l'utilisateur
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='kyc_profile'
        # Note: limit_choices_to removed for Swagger compatibility
    )
    
    # Informations personnelles étendues
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom de famille")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom du milieu")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    place_of_birth = models.CharField(max_length=200, verbose_name="Lieu de naissance")
    nationality = models.CharField(max_length=100, verbose_name="Nationalité")
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')],
        verbose_name="Genre"
    )
    
    # Adresse
    address_line_1 = models.CharField(max_length=200, verbose_name="Adresse ligne 1")
    address_line_2 = models.CharField(max_length=200, blank=True, null=True, verbose_name="Adresse ligne 2")
    city = models.CharField(max_length=100, verbose_name="Ville")
    state_province = models.CharField(max_length=100, verbose_name="État/Province")
    postal_code = models.CharField(max_length=20, verbose_name="Code postal")
    country = models.CharField(max_length=100, verbose_name="Pays")
    
    # Documents d'identité
    identity_document_type = models.CharField(
        max_length=50,
        choices=[
            ('PASSPORT', 'Passeport'),
            ('NATIONAL_ID', 'Carte d\'identité nationale'),
            ('DRIVER_LICENSE', 'Permis de conduire'),
            ('RESIDENCE_PERMIT', 'Titre de séjour'),
        ],
        verbose_name="Type de document d'identité"
    )
    identity_document_number = models.CharField(
        max_length=50, 
        verbose_name="Numéro du document d'identité"
    )
    identity_document_expiry = models.DateField(
        blank=True, null=True,
        verbose_name="Date d'expiration du document"
    )
    identity_document_issuing_country = models.CharField(
        max_length=100, 
        verbose_name="Pays d'émission du document"
    )
    
    # Informations professionnelles
    occupation = models.CharField(max_length=200, verbose_name="Profession")
    employer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom de l'employeur")
    monthly_income = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name="Revenus mensuels (FCFA)"
    )
    source_of_funds = models.CharField(
        max_length=100,
        choices=[
            ('SALARY', 'Salaire'),
            ('BUSINESS', 'Activité commerciale'),
            ('INVESTMENT', 'Investissements'),
            ('INHERITANCE', 'Héritage'),
            ('GIFT', 'Don'),
            ('OTHER', 'Autre'),
        ],
        verbose_name="Source des fonds"
    )
    
    # Statut KYC
    kyc_status = models.CharField(
        max_length=20, 
        choices=KYC_STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut KYC"
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVELS,
        default='LOW',
        verbose_name="Niveau de risque"
    )
    
    # Vérification des documents
    identity_verification_status = models.CharField(
        max_length=20,
        choices=DOCUMENT_VERIFICATION_STATUS,
        default='NOT_SUBMITTED',
        verbose_name="Statut vérification identité"
    )
    address_verification_status = models.CharField(
        max_length=20,
        choices=DOCUMENT_VERIFICATION_STATUS,
        default='NOT_SUBMITTED',
        verbose_name="Statut vérification adresse"
    )
    selfie_verification_status = models.CharField(
        max_length=20,
        choices=DOCUMENT_VERIFICATION_STATUS,
        default='NOT_SUBMITTED',
        verbose_name="Statut vérification selfie"
    )
    
    # Métadonnées de vérification
    verification_provider = models.CharField(
        max_length=50,
        choices=[
            ('SMILE_IDENTITY', 'Smile Identity'),
            ('ONFIDO', 'Onfido'),
            ('COMPLY_ADVANTAGE', 'ComplyAdvantage'),
            ('MANUAL', 'Vérification manuelle'),
        ],
        blank=True, null=True,
        verbose_name="Fournisseur de vérification"
    )
    verification_reference = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Référence de vérification externe"
    )
    verification_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de vérification (%)"
    )
    
    # Dates importantes
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de soumission")
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de révision")
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name="Date d'approbation")
    rejected_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de rejet")
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name="Date d'expiration")
    
    # Motifs de rejet
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de rejet")
    rejection_details = models.JSONField(
        default=dict, blank=True,
        verbose_name="Détails du rejet",
        help_text="Détails techniques du rejet (erreurs API, etc.)"
    )
    
    # Audit
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='reviewed_kyc_profiles',
        verbose_name="Révisé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil KYC"
        verbose_name_plural = "Profils KYC"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"KYC - {self.first_name} {self.last_name} ({self.get_kyc_status_display()})"
    
    @property
    def full_name(self):
        """Nom complet du client"""
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, names))
    
    @property
    def age(self):
        """Calcule l'âge du client"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def is_kyc_complete(self):
        """Vérifie si le KYC est complet"""
        required_fields = [
            self.first_name, self.last_name, self.date_of_birth,
            self.address_line_1, self.city, self.country,
            self.identity_document_type, self.identity_document_number,
            self.occupation
        ]
        return all(required_fields) and self.kyc_status == 'APPROVED'
    
    @property
    def completion_percentage(self):
        """Calcule le pourcentage de completion du profil KYC"""
        total_fields = 20  # Nombre total de champs importants
        completed_fields = 0
        
        # Champs obligatoires
        required_fields = [
            self.first_name, self.last_name, self.date_of_birth,
            self.address_line_1, self.city, self.country,
            self.identity_document_type, self.identity_document_number,
            self.occupation, self.nationality, self.place_of_birth
        ]
        completed_fields += sum(1 for field in required_fields if field)
        
        # Statuts de vérification
        if self.identity_verification_status in ['VERIFIED', 'SUBMITTED']:
            completed_fields += 3
        if self.address_verification_status in ['VERIFIED', 'SUBMITTED']:
            completed_fields += 3
        if self.selfie_verification_status in ['VERIFIED', 'SUBMITTED']:
            completed_fields += 3
        
        return min(100, (completed_fields / total_fields) * 100)
    
    def submit_for_review(self):
        """Soumet le profil KYC pour révision"""
        if self.kyc_status == 'PENDING':
            self.kyc_status = 'UNDER_REVIEW'
            self.submitted_at = timezone.now()
            self.save()
    
    def approve(self, reviewed_by_user, verification_provider=None, verification_score=None):
        """Approuve le profil KYC"""
        self.kyc_status = 'APPROVED'
        self.approved_at = timezone.now()
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by_user
        if verification_provider:
            self.verification_provider = verification_provider
        if verification_score:
            self.verification_score = verification_score
        self.save()
        
        # Marquer l'utilisateur comme vérifié
        self.user.is_verified = True
        self.user.save()
    
    def reject(self, reviewed_by_user, reason, details=None):
        """Rejette le profil KYC"""
        self.kyc_status = 'REJECTED'
        self.rejected_at = timezone.now()
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by_user
        self.rejection_reason = reason
        if details:
            self.rejection_details = details
        self.save()


class KYCDocument(models.Model):
    """
    Documents téléversés pour la vérification KYC
    """
    
    DOCUMENT_TYPES = [
        ('IDENTITY_FRONT', 'Pièce d\'identité (recto)'),
        ('IDENTITY_BACK', 'Pièce d\'identité (verso)'),
        ('SELFIE', 'Photo selfie'),
        ('PROOF_OF_ADDRESS', 'Justificatif de domicile'),
        ('BANK_STATEMENT', 'Relevé bancaire'),
        ('SALARY_SLIP', 'Fiche de paie'),
        ('OTHER', 'Autre document'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En cours de traitement'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
        ('EXPIRED', 'Expiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_profile = models.ForeignKey(
        KYCProfile, on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES,
        verbose_name="Type de document"
    )
    file = models.FileField(
        upload_to=kyc_document_upload_path,
        verbose_name="Fichier"
    )
    original_filename = models.CharField(max_length=255, verbose_name="Nom original du fichier")
    file_size = models.PositiveIntegerField(verbose_name="Taille du fichier (bytes)")
    mime_type = models.CharField(max_length=100, verbose_name="Type MIME")
    
    # Statut de vérification
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='PENDING',
        verbose_name="Statut de vérification"
    )
    
    # Métadonnées de vérification automatique
    auto_verification_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de vérification automatique (%)"
    )
    extracted_data = models.JSONField(
        default=dict, blank=True,
        verbose_name="Données extraites",
        help_text="Données extraites automatiquement du document (OCR, etc.)"
    )
    verification_details = models.JSONField(
        default=dict, blank=True,
        verbose_name="Détails de vérification",
        help_text="Détails techniques de la vérification (API response, etc.)"
    )
    
    # Audit
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='verified_documents',
        # Note: limit_choices_to removed for Swagger compatibility
        verbose_name="Vérifié par"
    )
    
    # Motifs de rejet
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de rejet")
    
    class Meta:
        verbose_name = "Document KYC"
        verbose_name_plural = "Documents KYC"
        ordering = ['-uploaded_at']
        unique_together = ['kyc_profile', 'document_type']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.kyc_profile.full_name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def verify(self, verified_by_user, score=None, extracted_data=None):
        """Marque le document comme vérifié"""
        self.verification_status = 'VERIFIED'
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        if score:
            self.auto_verification_score = score
        if extracted_data:
            self.extracted_data = extracted_data
        self.save()
    
    def reject(self, verified_by_user, reason):
        """Rejette le document"""
        self.verification_status = 'REJECTED'
        self.verified_at = timezone.now()
        self.verified_by = verified_by_user
        self.rejection_reason = reason
        self.save()


class KYCVerificationLog(models.Model):
    """
    Journal des vérifications KYC (pour audit et traçabilité)
    """
    
    ACTION_TYPES = [
        ('PROFILE_CREATED', 'Profil créé'),
        ('DOCUMENT_UPLOADED', 'Document téléversé'),
        ('DOCUMENT_VERIFIED', 'Document vérifié'),
        ('DOCUMENT_REJECTED', 'Document rejeté'),
        ('PROFILE_SUBMITTED', 'Profil soumis pour révision'),
        ('PROFILE_APPROVED', 'Profil approuvé'),
        ('PROFILE_REJECTED', 'Profil rejeté'),
        ('AUTO_VERIFICATION', 'Vérification automatique'),
        ('MANUAL_REVIEW', 'Révision manuelle'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_profile = models.ForeignKey(
        KYCProfile, on_delete=models.CASCADE,
        related_name='verification_logs'
    )
    
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name="Type d'action"
    )
    description = models.TextField(verbose_name="Description")
    
    # Métadonnées
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kyc_actions',
        verbose_name="Effectué par"
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Données contextuelles
    old_values = models.JSONField(
        default=dict, blank=True,
        verbose_name="Anciennes valeurs"
    )
    new_values = models.JSONField(
        default=dict, blank=True,
        verbose_name="Nouvelles valeurs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de vérification KYC"
        verbose_name_plural = "Logs de vérification KYC"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.kyc_profile.full_name} ({self.created_at})"
