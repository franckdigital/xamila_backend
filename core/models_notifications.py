"""
Modèles spécialisés pour le système de notifications
Notifications multi-canal, templates, campagnes, préférences utilisateur
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Templates de notifications réutilisables
    """
    
    TEMPLATE_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Notification push'),
        ('IN_APP', 'Notification in-app'),
        ('WEBHOOK', 'Webhook'),
    ]
    
    TEMPLATE_CATEGORIES = [
        ('SYSTEM', 'Système'),
        ('MARKETING', 'Marketing'),
        ('TRANSACTIONAL', 'Transactionnel'),
        ('EDUCATIONAL', 'Éducationnel'),
        ('SECURITY', 'Sécurité'),
        ('TRADING', 'Trading'),
        ('SGI', 'SGI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations du template
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    description = models.TextField(blank=True, verbose_name="Description")
    template_type = models.CharField(
        max_length=20, choices=TEMPLATE_TYPES,
        verbose_name="Type de template"
    )
    category = models.CharField(
        max_length=20, choices=TEMPLATE_CATEGORIES,
        verbose_name="Catégorie"
    )
    
    # Contenu du template
    subject_template = models.CharField(
        max_length=500, blank=True,
        verbose_name="Template du sujet"
    )
    body_template = models.TextField(verbose_name="Template du corps")
    html_template = models.TextField(
        blank=True, verbose_name="Template HTML"
    )
    
    # Variables disponibles
    available_variables = models.JSONField(
        default=list, blank=True,
        verbose_name="Variables disponibles",
        help_text="Liste des variables utilisables dans le template"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name="Template actif")
    is_default = models.BooleanField(default=False, verbose_name="Template par défaut")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_notification_templates'
    )
    
    class Meta:
        verbose_name = "Template de notification"
        verbose_name_plural = "Templates de notifications"
        ordering = ['category', 'name']
        unique_together = ['template_type', 'category', 'is_default']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class NotificationCampaign(models.Model):
    """
    Campagnes de notifications
    """
    
    CAMPAIGN_STATUS = [
        ('DRAFT', 'Brouillon'),
        ('SCHEDULED', 'Programmée'),
        ('ACTIVE', 'Active'),
        ('PAUSED', 'En pause'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    CAMPAIGN_TYPES = [
        ('ONE_TIME', 'Ponctuelle'),
        ('RECURRING', 'Récurrente'),
        ('TRIGGERED', 'Déclenchée'),
        ('DRIP', 'Séquentielle'),
    ]
    
    TARGET_AUDIENCES = [
        ('ALL_USERS', 'Tous les utilisateurs'),
        ('CUSTOMERS', 'Clients'),
        ('SGI_MANAGERS', 'Managers SGI'),
        ('INSTRUCTORS', 'Formateurs'),
        ('STUDENTS', 'Étudiants'),
        ('INACTIVE_USERS', 'Utilisateurs inactifs'),
        ('HIGH_VALUE', 'Clients à forte valeur'),
        ('CUSTOM', 'Audience personnalisée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de la campagne
    name = models.CharField(max_length=200, verbose_name="Nom de la campagne")
    description = models.TextField(blank=True, verbose_name="Description")
    campaign_type = models.CharField(
        max_length=20, choices=CAMPAIGN_TYPES,
        verbose_name="Type de campagne"
    )
    
    # Template utilisé
    template = models.ForeignKey(
        NotificationTemplate, on_delete=models.CASCADE,
        related_name='campaigns'
    )
    
    # Audience cible
    target_audience = models.CharField(
        max_length=20, choices=TARGET_AUDIENCES,
        verbose_name="Audience cible"
    )
    custom_audience_filter = models.JSONField(
        default=dict, blank=True,
        verbose_name="Filtre d'audience personnalisée"
    )
    
    # Programmation
    scheduled_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Programmée pour"
    )
    recurring_pattern = models.JSONField(
        default=dict, blank=True,
        verbose_name="Modèle de récurrence"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=CAMPAIGN_STATUS,
        default='DRAFT', verbose_name="Statut"
    )
    
    # Statistiques
    total_recipients = models.PositiveIntegerField(
        default=0, verbose_name="Nombre total de destinataires"
    )
    sent_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre envoyé"
    )
    delivered_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre livré"
    )
    opened_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre ouvert"
    )
    clicked_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de clics"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_campaigns'
    )
    
    class Meta:
        verbose_name = "Campagne de notification"
        verbose_name_plural = "Campagnes de notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def open_rate(self):
        """Calcule le taux d'ouverture"""
        if self.delivered_count > 0:
            return (self.opened_count / self.delivered_count) * 100
        return 0
    
    @property
    def click_rate(self):
        """Calcule le taux de clic"""
        if self.opened_count > 0:
            return (self.clicked_count / self.opened_count) * 100
        return 0


class Notification(models.Model):
    """
    Notifications individuelles
    """
    
    NOTIFICATION_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Notification push'),
        ('IN_APP', 'Notification in-app'),
        ('WEBHOOK', 'Webhook'),
    ]
    
    NOTIFICATION_STATUS = [
        ('PENDING', 'En attente'),
        ('SENT', 'Envoyée'),
        ('DELIVERED', 'Livrée'),
        ('OPENED', 'Ouverte'),
        ('CLICKED', 'Cliquée'),
        ('FAILED', 'Échec'),
        ('BOUNCED', 'Rejetée'),
        ('SPAM', 'Spam'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Faible'),
        ('NORMAL', 'Normale'),
        ('HIGH', 'Élevée'),
        ('URGENT', 'Urgente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Destinataire
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    
    # Campagne associée (optionnel)
    campaign = models.ForeignKey(
        NotificationCampaign, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='notifications'
    )
    
    # Type et contenu
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES,
        verbose_name="Type de notification"
    )
    subject = models.CharField(max_length=500, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    html_content = models.TextField(blank=True, verbose_name="Contenu HTML")
    
    # Métadonnées
    data = models.JSONField(
        default=dict, blank=True,
        verbose_name="Données additionnelles"
    )
    
    # Configuration
    priority = models.CharField(
        max_length=10, choices=PRIORITY_LEVELS,
        default='NORMAL', verbose_name="Priorité"
    )
    
    # Statut et suivi
    status = models.CharField(
        max_length=20, choices=NOTIFICATION_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    
    # Programmation
    scheduled_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Programmée pour"
    )
    
    # Suivi des événements
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    opened_at = models.DateTimeField(blank=True, null=True)
    clicked_at = models.DateTimeField(blank=True, null=True)
    
    # Informations d'erreur
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    retry_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de tentatives"
    )
    max_retries = models.PositiveIntegerField(
        default=3, verbose_name="Nombre maximum de tentatives"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient.full_name}: {self.subject[:50]}"


class NotificationPreference(models.Model):
    """
    Préférences de notification des utilisateurs
    """
    
    NOTIFICATION_CHANNELS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Notification push'),
        ('IN_APP', 'Notification in-app'),
    ]
    
    NOTIFICATION_CATEGORIES = [
        ('SYSTEM', 'Notifications système'),
        ('MARKETING', 'Marketing'),
        ('EDUCATIONAL', 'Éducationnel'),
        ('TRADING', 'Trading'),
        ('SGI', 'SGI'),
        ('SECURITY', 'Sécurité'),
        ('REMINDERS', 'Rappels'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Préférences par canal et catégorie
    preferences = models.JSONField(
        default=dict,
        verbose_name="Préférences de notification",
        help_text="Structure: {channel: {category: boolean}}"
    )
    
    # Paramètres globaux
    global_opt_out = models.BooleanField(
        default=False,
        verbose_name="Désabonnement global"
    )
    
    # Heures de silence
    quiet_hours_start = models.TimeField(
        blank=True, null=True,
        verbose_name="Début des heures de silence"
    )
    quiet_hours_end = models.TimeField(
        blank=True, null=True,
        verbose_name="Fin des heures de silence"
    )
    
    # Fréquence
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('IMMEDIATE', 'Immédiat'),
            ('HOURLY', 'Horaire'),
            ('DAILY', 'Quotidien'),
            ('WEEKLY', 'Hebdomadaire'),
        ],
        default='IMMEDIATE',
        verbose_name="Fréquence de résumé"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Préférence de notification"
        verbose_name_plural = "Préférences de notifications"
    
    def __str__(self):
        return f"Préférences de {self.user.full_name}"
    
    def is_channel_enabled(self, channel, category):
        """Vérifie si un canal est activé pour une catégorie"""
        if self.global_opt_out:
            return False
        return self.preferences.get(channel, {}).get(category, True)


class NotificationLog(models.Model):
    """
    Journal des notifications pour audit et debugging
    """
    
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Informations du log
    level = models.CharField(
        max_length=20, choices=LOG_LEVELS,
        verbose_name="Niveau de log"
    )
    message = models.TextField(verbose_name="Message")
    details = models.JSONField(
        default=dict, blank=True,
        verbose_name="Détails additionnels"
    )
    
    # Métadonnées
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de notification"
        verbose_name_plural = "Logs de notifications"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.level} - {self.message[:50]}"


class WebhookEndpoint(models.Model):
    """
    Endpoints webhook pour les notifications externes
    """
    
    WEBHOOK_STATUS = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('FAILED', 'En échec'),
        ('SUSPENDED', 'Suspendu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Configuration du webhook
    name = models.CharField(max_length=200, verbose_name="Nom du webhook")
    url = models.URLField(verbose_name="URL du webhook")
    secret_key = models.CharField(
        max_length=255, blank=True,
        verbose_name="Clé secrète"
    )
    
    # Événements écoutés
    events = models.JSONField(
        default=list,
        verbose_name="Événements écoutés"
    )
    
    # Configuration
    timeout = models.PositiveIntegerField(
        default=30, verbose_name="Timeout (secondes)"
    )
    max_retries = models.PositiveIntegerField(
        default=3, verbose_name="Nombre maximum de tentatives"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=WEBHOOK_STATUS,
        default='ACTIVE', verbose_name="Statut"
    )
    
    # Statistiques
    total_calls = models.PositiveIntegerField(
        default=0, verbose_name="Nombre total d'appels"
    )
    successful_calls = models.PositiveIntegerField(
        default=0, verbose_name="Appels réussis"
    )
    failed_calls = models.PositiveIntegerField(
        default=0, verbose_name="Appels échoués"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_called_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_webhooks'
    )
    
    class Meta:
        verbose_name = "Endpoint webhook"
        verbose_name_plural = "Endpoints webhook"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.url}"
    
    @property
    def success_rate(self):
        """Calcule le taux de succès"""
        if self.total_calls > 0:
            return (self.successful_calls / self.total_calls) * 100
        return 0


class NotificationQueue(models.Model):
    """
    File d'attente des notifications
    """
    
    QUEUE_STATUS = [
        ('QUEUED', 'En file'),
        ('PROCESSING', 'En cours de traitement'),
        ('PROCESSED', 'Traité'),
        ('FAILED', 'Échec'),
        ('RETRYING', 'Nouvelle tentative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.OneToOneField(
        Notification, on_delete=models.CASCADE,
        related_name='queue_entry'
    )
    
    # Statut de la file
    status = models.CharField(
        max_length=20, choices=QUEUE_STATUS,
        default='QUEUED', verbose_name="Statut"
    )
    
    # Priorité dans la file
    priority = models.PositiveIntegerField(
        default=100, verbose_name="Priorité",
        help_text="Plus le nombre est faible, plus la priorité est élevée"
    )
    
    # Tentatives
    attempts = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de tentatives"
    )
    next_retry_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Prochaine tentative"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "File de notification"
        verbose_name_plural = "Files de notifications"
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['next_retry_at']),
        ]
    
    def __str__(self):
        return f"Queue entry for {self.notification.id} - {self.status}"
