"""
Modèles spécialisés pour la gestion des contrats
Workflow avancé, signatures électroniques, conformité
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

from .models import SGI  # Import du modèle SGI de base

User = get_user_model()


class ContractTemplate(models.Model):
    """
    Modèles de contrats personnalisables par SGI
    """
    
    TEMPLATE_TYPES = [
        ('STANDARD', 'Contrat standard'),
        ('PREMIUM', 'Contrat premium'),
        ('CORPORATE', 'Contrat entreprise'),
        ('CUSTOM', 'Contrat personnalisé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sgi = models.ForeignKey(SGI, on_delete=models.CASCADE, related_name='contract_templates')
    
    # Informations du template
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    template_type = models.CharField(
        max_length=20, choices=TEMPLATE_TYPES,
        verbose_name="Type de template"
    )
    
    # Contenu du contrat
    content = models.TextField(verbose_name="Contenu du contrat")
    variables = models.JSONField(
        default=dict,
        verbose_name="Variables du template",
        help_text="Variables à remplacer dans le contrat (ex: {client_name})"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name="Template actif")
    requires_signature = models.BooleanField(default=True, verbose_name="Signature requise")
    auto_approval_threshold = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name="Seuil d'approbation automatique (FCFA)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_contract_templates'
    )
    
    class Meta:
        verbose_name = "Template de contrat"
        verbose_name_plural = "Templates de contrats"
        ordering = ['-created_at']
        unique_together = ['sgi', 'name']
    
    def __str__(self):
        return f"{self.sgi.name} - {self.name}"


class ContractExtended(models.Model):
    """
    Extension du modèle Contract avec fonctionnalités avancées
    """
    
    PRIORITY_LEVELS = [
        ('LOW', 'Faible'),
        ('NORMAL', 'Normale'),
        ('HIGH', 'Élevée'),
        ('URGENT', 'Urgente'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Risque faible'),
        ('MEDIUM', 'Risque moyen'),
        ('HIGH', 'Risque élevé'),
        ('CRITICAL', 'Risque critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation avec le contrat de base (si on garde la compatibilité)
    base_contract = models.OneToOneField(
        'Contract', on_delete=models.CASCADE, blank=True, null=True,
        related_name='extended_contract'
    )
    
    # Template utilisé
    template = models.ForeignKey(
        ContractTemplate, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='contracts'
    )
    
    # Workflow avancé
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS,
        default='NORMAL', verbose_name="Priorité"
    )
    
    risk_level = models.CharField(
        max_length=20, choices=RISK_LEVELS,
        default='LOW', verbose_name="Niveau de risque"
    )
    
    # Approbations multiples
    requires_legal_approval = models.BooleanField(
        default=False, verbose_name="Approbation légale requise"
    )
    requires_compliance_approval = models.BooleanField(
        default=False, verbose_name="Approbation conformité requise"
    )
    requires_manager_approval = models.BooleanField(
        default=True, verbose_name="Approbation manager requise"
    )
    
    # Signatures électroniques
    client_signature_required = models.BooleanField(
        default=True, verbose_name="Signature client requise"
    )
    manager_signature_required = models.BooleanField(
        default=True, verbose_name="Signature manager requise"
    )
    
    # Dates limites
    due_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Date limite de traitement"
    )
    client_response_deadline = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Délai de réponse client"
    )
    
    # Documents associés
    supporting_documents = models.JSONField(
        default=list,
        verbose_name="Documents justificatifs",
        help_text="Liste des URLs des documents"
    )
    
    # Conformité réglementaire
    kyc_verified = models.BooleanField(default=False, verbose_name="KYC vérifié")
    aml_checked = models.BooleanField(default=False, verbose_name="Contrôle AML effectué")
    regulatory_approval = models.BooleanField(default=False, verbose_name="Approbation réglementaire")
    
    # Métadonnées étendues
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contrat étendu"
        verbose_name_plural = "Contrats étendus"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Contrat étendu - {self.priority} - {self.risk_level}"
    
    def calculate_processing_time(self):
        """Calcule le temps de traitement estimé"""
        base_time = 24  # 24 heures de base
        
        if self.risk_level == 'CRITICAL':
            base_time *= 3
        elif self.risk_level == 'HIGH':
            base_time *= 2
        elif self.risk_level == 'MEDIUM':
            base_time *= 1.5
        
        if self.requires_legal_approval:
            base_time += 48
        if self.requires_compliance_approval:
            base_time += 24
        
        return timedelta(hours=base_time)
    
    def is_overdue(self):
        """Vérifie si le contrat est en retard"""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date


class ContractApproval(models.Model):
    """
    Historique des approbations de contrats
    """
    
    APPROVAL_TYPES = [
        ('MANAGER', 'Approbation manager'),
        ('LEGAL', 'Approbation légale'),
        ('COMPLIANCE', 'Approbation conformité'),
        ('FINAL', 'Approbation finale'),
    ]
    
    APPROVAL_STATUS = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('CONDITIONAL', 'Conditionnel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        ContractExtended, on_delete=models.CASCADE,
        related_name='approvals'
    )
    
    # Type d'approbation
    approval_type = models.CharField(
        max_length=20, choices=APPROVAL_TYPES,
        verbose_name="Type d'approbation"
    )
    
    # Approbateur
    approver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='contract_approvals'
    )
    
    # Statut et détails
    status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    
    comments = models.TextField(blank=True, verbose_name="Commentaires")
    conditions = models.TextField(blank=True, verbose_name="Conditions")
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Approbation de contrat"
        verbose_name_plural = "Approbations de contrats"
        ordering = ['-requested_at']
        unique_together = ['contract', 'approval_type', 'approver']
    
    def __str__(self):
        return f"{self.approval_type} - {self.approver.full_name} - {self.status}"


class ElectronicSignature(models.Model):
    """
    Signatures électroniques des contrats
    """
    
    SIGNATURE_TYPES = [
        ('CLIENT', 'Signature client'),
        ('MANAGER', 'Signature manager'),
        ('WITNESS', 'Signature témoin'),
        ('LEGAL', 'Signature légale'),
    ]
    
    SIGNATURE_STATUS = [
        ('PENDING', 'En attente'),
        ('SIGNED', 'Signé'),
        ('REJECTED', 'Rejeté'),
        ('EXPIRED', 'Expiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        ContractExtended, on_delete=models.CASCADE,
        related_name='signatures'
    )
    
    # Signataire
    signer = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='electronic_signatures'
    )
    
    signature_type = models.CharField(
        max_length=20, choices=SIGNATURE_TYPES,
        verbose_name="Type de signature"
    )
    
    # Statut et métadonnées
    status = models.CharField(
        max_length=20, choices=SIGNATURE_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    
    # Données de signature
    signature_data = models.TextField(
        blank=True, verbose_name="Données de signature",
        help_text="Hash ou données cryptographiques de la signature"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True, null=True,
        verbose_name="Adresse IP"
    )
    
    user_agent = models.TextField(
        blank=True, verbose_name="User Agent"
    )
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Date d'expiration"
    )
    
    class Meta:
        verbose_name = "Signature électronique"
        verbose_name_plural = "Signatures électroniques"
        ordering = ['-requested_at']
        unique_together = ['contract', 'signer', 'signature_type']
    
    def __str__(self):
        return f"{self.signature_type} - {self.signer.full_name} - {self.status}"
    
    def is_expired(self):
        """Vérifie si la demande de signature a expiré"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class ContractAuditLog(models.Model):
    """
    Journal d'audit des modifications de contrats
    """
    
    ACTION_TYPES = [
        ('CREATED', 'Création'),
        ('UPDATED', 'Modification'),
        ('APPROVED', 'Approbation'),
        ('REJECTED', 'Rejet'),
        ('SIGNED', 'Signature'),
        ('CANCELLED', 'Annulation'),
        ('ARCHIVED', 'Archivage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        ContractExtended, on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    # Action effectuée
    action = models.CharField(
        max_length=20, choices=ACTION_TYPES,
        verbose_name="Action"
    )
    
    # Utilisateur responsable
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='contract_audit_logs'
    )
    
    # Détails de l'action
    description = models.TextField(verbose_name="Description")
    old_values = models.JSONField(
        default=dict, blank=True,
        verbose_name="Anciennes valeurs"
    )
    new_values = models.JSONField(
        default=dict, blank=True,
        verbose_name="Nouvelles valeurs"
    )
    
    # Métadonnées
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Log d'audit contrat"
        verbose_name_plural = "Logs d'audit contrats"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.user.full_name} - {self.timestamp}"
