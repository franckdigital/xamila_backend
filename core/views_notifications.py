"""
Vues API pour le module Notifications
Endpoints REST pour la gestion des notifications
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal

from .models_notifications import (
    NotificationTemplate, NotificationCampaign, Notification,
    NotificationPreference, NotificationLog, WebhookEndpoint,
    NotificationQueue
)
from .serializers_notifications import (
    NotificationTemplateSerializer, NotificationCampaignSerializer,
    NotificationSerializer, NotificationPreferenceSerializer,
    NotificationLogSerializer, WebhookEndpointSerializer,
    NotificationQueueSerializer, NotificationTemplateCreateSerializer,
    NotificationCampaignCreateSerializer, NotificationCreateSerializer,
    WebhookEndpointCreateSerializer, NotificationPreferenceUpdateSerializer,
    NotificationStatsSerializer, CampaignStatsSerializer
)

User = get_user_model()


class NotificationTemplateListView(generics.ListCreateAPIView):
    """Templates de notifications"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationTemplateCreateSerializer
        return NotificationTemplateSerializer
    
    def get_queryset(self):
        queryset = NotificationTemplate.objects.all()
        
        # Filtres
        template_type = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        is_active = self.request.query_params.get('active')
        search = self.request.query_params.get('search')
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        if category:
            queryset = queryset.filter(category=category)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('category', 'name')
    
    def perform_create(self, serializer):
        if not self.request.user.role in ['ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les administrateurs peuvent créer des templates"
            )
        serializer.save(created_by=self.request.user)


class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détails d'un template de notification"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationCampaignListView(generics.ListCreateAPIView):
    """Campagnes de notifications"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCampaignCreateSerializer
        return NotificationCampaignSerializer
    
    def get_queryset(self):
        queryset = NotificationCampaign.objects.all()
        
        # Filtres
        campaign_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.select_related('template', 'created_by').order_by('-created_at')
    
    def perform_create(self, serializer):
        if not self.request.user.role in ['ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les administrateurs peuvent créer des campagnes"
            )
        campaign = serializer.save(created_by=self.request.user)
        _calculate_campaign_recipients(campaign)


class NotificationCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détails d'une campagne de notification"""
    queryset = NotificationCampaign.objects.all()
    serializer_class = NotificationCampaignSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_campaign(request, campaign_id):
    """Démarrer une campagne de notifications"""
    if not request.user.role in ['ADMIN', 'SUPPORT']:
        return Response(
            {'error': 'Seuls les administrateurs peuvent démarrer des campagnes'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        campaign = NotificationCampaign.objects.get(id=campaign_id)
    except NotificationCampaign.DoesNotExist:
        return Response(
            {'error': 'Campagne introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if campaign.status != 'DRAFT':
        return Response(
            {'error': 'Seules les campagnes en brouillon peuvent être démarrées'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    campaign.status = 'ACTIVE'
    campaign.started_at = timezone.now()
    campaign.save()
    
    recipients = _get_campaign_recipients(campaign)
    notifications_created = _create_campaign_notifications(campaign, recipients)
    
    campaign.total_recipients = len(recipients)
    campaign.save()
    
    return Response({
        'message': 'Campagne démarrée avec succès',
        'campaign': NotificationCampaignSerializer(campaign).data,
        'notifications_created': notifications_created
    })


class NotificationListView(generics.ListCreateAPIView):
    """Notifications"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        queryset = Notification.objects.all()
        
        # Filtrer par utilisateur si pas admin
        if self.request.user.role not in ['ADMIN', 'SUPPORT']:
            queryset = queryset.filter(recipient=self.request.user)
        
        # Filtres
        notification_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('recipient', 'campaign').order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détails d'une notification"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.all()
        if self.request.user.role not in ['ADMIN', 'SUPPORT']:
            queryset = queryset.filter(recipient=self.request.user)
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if notification.status == 'DELIVERED' and not notification.opened_at:
        notification.opened_at = timezone.now()
        notification.save()
    
    return Response({
        'message': 'Notification marquée comme lue',
        'notification': NotificationSerializer(notification).data
    })


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Préférences de notification de l'utilisateur"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user,
            defaults={
                'preferences': _get_default_preferences(),
                'digest_frequency': 'DAILY'
            }
        )
        return preferences


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_notifications(request):
    """Notifications de l'utilisateur connecté"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('campaign').order_by('-created_at')
    
    # Filtres
    unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        notifications = notifications.filter(opened_at__isnull=True)
    
    # Pagination simple
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    offset = (page - 1) * page_size
    
    total_count = notifications.count()
    notifications_page = notifications[offset:offset + page_size]
    
    unread_count = Notification.objects.filter(
        recipient=request.user,
        opened_at__isnull=True
    ).count()
    
    return Response({
        'notifications': NotificationSerializer(notifications_page, many=True).data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': (total_count + page_size - 1) // page_size
        },
        'stats': {
            'unread_count': unread_count,
            'total_count': total_count
        }
    })


class WebhookEndpointListView(generics.ListCreateAPIView):
    """Endpoints webhook"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WebhookEndpointCreateSerializer
        return WebhookEndpointSerializer
    
    def get_queryset(self):
        if self.request.user.role not in ['ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les administrateurs peuvent gérer les webhooks"
            )
        return WebhookEndpoint.objects.all().order_by('name')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Statistiques globales des notifications"""
    if not request.user.role in ['ADMIN', 'SUPPORT']:
        return Response(
            {'error': 'Accès non autorisé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    notifications = Notification.objects.filter(created_at__gte=start_date)
    
    total_sent = notifications.filter(status__in=['SENT', 'DELIVERED']).count()
    total_delivered = notifications.filter(status='DELIVERED').count()
    total_opened = notifications.filter(opened_at__isnull=False).count()
    total_failed = notifications.filter(status='FAILED').count()
    
    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    
    stats = {
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_opened': total_opened,
        'total_failed': total_failed,
        'delivery_rate': round(delivery_rate, 2),
        'open_rate': round(open_rate, 2)
    }
    
    return Response({
        'period_days': days,
        'stats': stats
    })


# Fonctions utilitaires

def _calculate_campaign_recipients(campaign):
    """Calculer le nombre de destinataires d'une campagne"""
    recipients = _get_campaign_recipients(campaign)
    campaign.total_recipients = len(recipients)
    campaign.save()


def _get_campaign_recipients(campaign):
    """Récupérer la liste des destinataires d'une campagne"""
    if campaign.target_audience == 'ALL_USERS':
        return User.objects.filter(is_active=True)
    elif campaign.target_audience == 'CUSTOMERS':
        return User.objects.filter(role='CUSTOMER', is_active=True)
    elif campaign.target_audience == 'SGI_MANAGERS':
        return User.objects.filter(role='SGI_MANAGER', is_active=True)
    elif campaign.target_audience == 'STUDENTS':
        return User.objects.filter(role='STUDENT', is_active=True)
    elif campaign.target_audience == 'CUSTOM':
        queryset = User.objects.filter(is_active=True)
        filters = campaign.custom_audience_filter
        
        if 'roles' in filters:
            queryset = queryset.filter(role__in=filters['roles'])
        if 'registration_date_after' in filters:
            queryset = queryset.filter(date_joined__gte=filters['registration_date_after'])
        
        return queryset
    
    return User.objects.none()


def _create_campaign_notifications(campaign, recipients):
    """Créer les notifications pour une campagne"""
    template = campaign.template
    notifications_created = 0
    
    for recipient in recipients:
        if not _should_send_notification(recipient, template.category):
            continue
        
        context = _get_notification_context(recipient)
        subject = _render_template(template.subject_template, context)
        message = _render_template(template.body_template, context)
        
        notification = Notification.objects.create(
            recipient=recipient,
            campaign=campaign,
            notification_type=template.template_type,
            subject=subject,
            message=message,
            priority='NORMAL',
            scheduled_at=campaign.scheduled_at
        )
        
        NotificationQueue.objects.create(
            notification=notification,
            priority=notification.priority
        )
        
        notifications_created += 1
    
    return notifications_created


def _should_send_notification(user, category):
    """Vérifier si une notification doit être envoyée"""
    try:
        preferences = NotificationPreference.objects.get(user=user)
        if preferences.global_opt_out:
            return False
        
        user_prefs = preferences.preferences
        if category in user_prefs.get('EMAIL', {}):
            return user_prefs['EMAIL'][category]
        
        return True
    except NotificationPreference.DoesNotExist:
        return True


def _get_notification_context(user):
    """Récupérer le contexte pour personnaliser une notification"""
    return {
        'user_name': user.get_full_name() or user.username,
        'user_email': user.email,
        'user_first_name': user.first_name,
        'user_last_name': user.last_name,
        'current_date': timezone.now().strftime('%d/%m/%Y'),
    }


def _render_template(template_string, context):
    """Rendre un template avec le contexte donné"""
    if not template_string:
        return ''
    
    try:
        from django.template import Template, Context
        template = Template(template_string)
        return template.render(Context(context))
    except Exception:
        return template_string


def _get_default_preferences():
    """Récupérer les préférences par défaut"""
    return {
        'EMAIL': {
            'SYSTEM': True,
            'MARKETING': True,
            'EDUCATIONAL': True,
            'TRADING': True,
            'SGI': True,
            'SECURITY': True,
            'REMINDERS': True
        },
        'SMS': {
            'SYSTEM': True,
            'MARKETING': False,
            'EDUCATIONAL': False,
            'TRADING': True,
            'SGI': True,
            'SECURITY': True,
            'REMINDERS': False
        },
        'PUSH': {
            'SYSTEM': True,
            'MARKETING': True,
            'EDUCATIONAL': True,
            'TRADING': True,
            'SGI': True,
            'SECURITY': True,
            'REMINDERS': True
        }
    }
