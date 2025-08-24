"""
Serializers pour le module Notifications
Sérialisation des données pour l'API REST de notifications
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime

from .models_notifications import (
    NotificationTemplate, NotificationCampaign, Notification,
    NotificationPreference, NotificationLog, WebhookEndpoint,
    NotificationQueue
)

User = get_user_model()


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer pour les templates de notifications
    """
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Statistiques d'utilisation
    campaigns_count = serializers.SerializerMethodField()
    
    # Affichage des choix
    template_type_display = serializers.CharField(
        source='get_template_type_display', read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'category',
            'subject_template', 'body_template', 'html_template',
            'available_variables', 'is_active', 'is_default',
            'created_at', 'updated_at', 'created_by_name',
            'campaigns_count', 'template_type_display', 'category_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_campaigns_count(self, obj):
        """Nombre de campagnes utilisant ce template"""
        return obj.campaigns.count()
    
    def validate(self, data):
        """Validation des données du template"""
        template_type = data.get('template_type')
        subject_template = data.get('subject_template', '')
        body_template = data.get('body_template', '')
        
        # Le sujet est requis pour les emails
        if template_type == 'EMAIL' and not subject_template.strip():
            raise serializers.ValidationError(
                "Le sujet est requis pour les templates d'email"
            )
        
        # Le corps est toujours requis
        if not body_template.strip():
            raise serializers.ValidationError(
                "Le corps du message est requis"
            )
        
        return data


class NotificationCampaignSerializer(serializers.ModelSerializer):
    """
    Serializer pour les campagnes de notifications
    """
    
    # Informations du template
    template_name = serializers.CharField(
        source='template.name', read_only=True
    )
    template_type = serializers.CharField(
        source='template.template_type', read_only=True
    )
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Métriques calculées
    delivery_rate = serializers.SerializerMethodField()
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()
    
    # Affichage des choix
    campaign_type_display = serializers.CharField(
        source='get_campaign_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    target_audience_display = serializers.CharField(
        source='get_target_audience_display', read_only=True
    )
    
    class Meta:
        model = NotificationCampaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'template',
            'target_audience', 'custom_audience_filter', 'scheduled_at',
            'recurring_pattern', 'status', 'total_recipients', 'sent_count',
            'delivered_count', 'opened_count', 'clicked_count',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'template_name', 'template_type', 'created_by_name',
            'delivery_rate', 'open_rate', 'click_rate',
            'campaign_type_display', 'status_display', 'target_audience_display'
        ]
        read_only_fields = [
            'id', 'total_recipients', 'sent_count', 'delivered_count',
            'opened_count', 'clicked_count', 'created_at', 'updated_at',
            'started_at', 'completed_at'
        ]
    
    def get_delivery_rate(self, obj):
        """Taux de livraison"""
        if obj.sent_count > 0:
            return (obj.delivered_count / obj.sent_count) * 100
        return 0
    
    def validate_scheduled_at(self, value):
        """Validation de la date de programmation"""
        if value and value <= datetime.now():
            raise serializers.ValidationError(
                "La date de programmation doit être dans le futur"
            )
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les notifications individuelles
    """
    
    # Informations du destinataire
    recipient_name = serializers.CharField(
        source='recipient.full_name', read_only=True
    )
    recipient_email = serializers.CharField(
        source='recipient.email', read_only=True
    )
    
    # Informations de la campagne
    campaign_name = serializers.CharField(
        source='campaign.name', read_only=True
    )
    
    # Affichage des choix
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'campaign', 'notification_type', 'subject',
            'message', 'html_content', 'data', 'priority', 'status',
            'scheduled_at', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'error_message', 'retry_count', 'max_retries', 'created_at', 'updated_at',
            'recipient_name', 'recipient_email', 'campaign_name',
            'notification_type_display', 'status_display', 'priority_display'
        ]
        read_only_fields = [
            'id', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'error_message', 'retry_count', 'created_at', 'updated_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les préférences de notification
    """
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    
    # Affichage des choix
    digest_frequency_display = serializers.CharField(
        source='get_digest_frequency_display', read_only=True
    )
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'preferences', 'global_opt_out',
            'quiet_hours_start', 'quiet_hours_end', 'digest_frequency',
            'created_at', 'updated_at', 'user_name', 'digest_frequency_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_preferences(self, value):
        """Validation de la structure des préférences"""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Les préférences doivent être un objet JSON"
            )
        
        # Valider la structure attendue
        valid_channels = ['EMAIL', 'SMS', 'PUSH', 'IN_APP']
        valid_categories = ['SYSTEM', 'MARKETING', 'EDUCATIONAL', 'TRADING', 'SGI', 'SECURITY', 'REMINDERS']
        
        for channel, categories in value.items():
            if channel not in valid_channels:
                raise serializers.ValidationError(
                    f"Canal invalide: {channel}"
                )
            
            if not isinstance(categories, dict):
                raise serializers.ValidationError(
                    f"Les catégories du canal {channel} doivent être un objet"
                )
            
            for category, enabled in categories.items():
                if category not in valid_categories:
                    raise serializers.ValidationError(
                        f"Catégorie invalide: {category}"
                    )
                
                if not isinstance(enabled, bool):
                    raise serializers.ValidationError(
                        f"La valeur pour {channel}.{category} doit être un booléen"
                    )
        
        return value


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Serializer pour les logs de notifications
    """
    
    # Informations de la notification
    notification_subject = serializers.CharField(
        source='notification.subject', read_only=True
    )
    notification_type = serializers.CharField(
        source='notification.notification_type', read_only=True
    )
    
    # Affichage des choix
    level_display = serializers.CharField(
        source='get_level_display', read_only=True
    )
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'level', 'message', 'details', 'timestamp',
            'notification_subject', 'notification_type', 'level_display'
        ]
        read_only_fields = ['id', 'timestamp']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """
    Serializer pour les endpoints webhook
    """
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Métriques calculées
    success_rate = serializers.ReadOnlyField()
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'name', 'url', 'secret_key', 'events', 'timeout',
            'max_retries', 'status', 'total_calls', 'successful_calls',
            'failed_calls', 'created_at', 'updated_at', 'last_called_at',
            'created_by_name', 'success_rate', 'status_display'
        ]
        read_only_fields = [
            'id', 'total_calls', 'successful_calls', 'failed_calls',
            'created_at', 'updated_at', 'last_called_at', 'success_rate'
        ]
    
    def validate_url(self, value):
        """Validation de l'URL du webhook"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "L'URL doit commencer par http:// ou https://"
            )
        return value
    
    def validate_events(self, value):
        """Validation des événements écoutés"""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError(
                "Au moins un événement doit être spécifié"
            )
        
        valid_events = [
            'notification.sent', 'notification.delivered', 'notification.opened',
            'notification.clicked', 'notification.failed', 'campaign.started',
            'campaign.completed', 'user.registered', 'user.updated'
        ]
        
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(
                    f"Événement invalide: {event}"
                )
        
        return value


class NotificationQueueSerializer(serializers.ModelSerializer):
    """
    Serializer pour la file d'attente des notifications
    """
    
    # Informations de la notification
    notification_subject = serializers.CharField(
        source='notification.subject', read_only=True
    )
    notification_type = serializers.CharField(
        source='notification.notification_type', read_only=True
    )
    recipient_name = serializers.CharField(
        source='notification.recipient.full_name', read_only=True
    )
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = NotificationQueue
        fields = [
            'id', 'notification', 'status', 'priority', 'attempts',
            'next_retry_at', 'created_at', 'updated_at', 'processed_at',
            'notification_subject', 'notification_type', 'recipient_name',
            'status_display'
        ]
        read_only_fields = [
            'id', 'attempts', 'created_at', 'updated_at', 'processed_at'
        ]


# Serializers pour la création et mise à jour

class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de templates
    """
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'name', 'description', 'template_type', 'category',
            'subject_template', 'body_template', 'html_template',
            'available_variables', 'is_default'
        ]
    
    def validate_name(self, value):
        """Validation du nom du template"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Le nom doit contenir au moins 3 caractères"
            )
        return value.strip()


class NotificationCampaignCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de campagnes
    """
    
    class Meta:
        model = NotificationCampaign
        fields = [
            'name', 'description', 'campaign_type', 'template',
            'target_audience', 'custom_audience_filter', 'scheduled_at',
            'recurring_pattern'
        ]
    
    def validate(self, data):
        """Validation croisée des données"""
        target_audience = data.get('target_audience')
        custom_audience_filter = data.get('custom_audience_filter', {})
        
        if target_audience == 'CUSTOM' and not custom_audience_filter:
            raise serializers.ValidationError(
                "Un filtre d'audience personnalisée est requis"
            )
        
        campaign_type = data.get('campaign_type')
        recurring_pattern = data.get('recurring_pattern', {})
        
        if campaign_type == 'RECURRING' and not recurring_pattern:
            raise serializers.ValidationError(
                "Un modèle de récurrence est requis pour les campagnes récurrentes"
            )
        
        return data


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de notifications
    """
    
    class Meta:
        model = Notification
        fields = [
            'recipient', 'notification_type', 'subject', 'message',
            'html_content', 'data', 'priority', 'scheduled_at'
        ]
    
    def validate_message(self, value):
        """Validation du message"""
        if not value.strip():
            raise serializers.ValidationError(
                "Le message ne peut pas être vide"
            )
        return value.strip()


class WebhookEndpointCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'endpoints webhook
    """
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'name', 'url', 'secret_key', 'events', 'timeout', 'max_retries'
        ]
    
    def validate_name(self, value):
        """Validation du nom"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Le nom doit contenir au moins 3 caractères"
            )
        return value.strip()


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des préférences
    """
    
    class Meta:
        model = NotificationPreference
        fields = [
            'preferences', 'global_opt_out', 'quiet_hours_start',
            'quiet_hours_end', 'digest_frequency'
        ]
    
    def validate_quiet_hours(self, data):
        """Validation des heures de silence"""
        start = data.get('quiet_hours_start')
        end = data.get('quiet_hours_end')
        
        if start and end and start >= end:
            raise serializers.ValidationError(
                "L'heure de fin doit être après l'heure de début"
            )
        
        return data


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques de notifications
    """
    
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_opened = serializers.IntegerField()
    total_clicked = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    delivery_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    open_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    click_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    failure_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class CampaignStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques de campagnes
    """
    
    campaign_id = serializers.UUIDField()
    campaign_name = serializers.CharField()
    sent_count = serializers.IntegerField()
    delivered_count = serializers.IntegerField()
    opened_count = serializers.IntegerField()
    clicked_count = serializers.IntegerField()
    delivery_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    open_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    click_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
