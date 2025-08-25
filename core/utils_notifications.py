"""
Utilitaires pour créer et gérer les notifications
"""

from django.utils import timezone
from .models_notifications import Notification, NotificationTemplate
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(recipient, notification_type, subject, message, data=None, priority='NORMAL'):
    """
    Créer une nouvelle notification
    """
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        subject=subject,
        message=message,
        data=data or {},
        priority=priority,
        status='SENT' if notification_type == 'IN_APP' else 'PENDING'
    )
    
    if notification_type == 'IN_APP':
        notification.sent_at = timezone.now()
        notification.delivered_at = timezone.now()
        notification.save()
    
    return notification


def create_system_notifications():
    """
    Créer des notifications système par défaut pour les utilisateurs
    """
    notifications_data = [
        {
            'subject': 'Challenge Semestriel disponible',
            'message': 'Rejoignez le nouveau challenge d\'épargne 6 mois',
            'data': {'type': 'challenge', 'action': 'join'}
        },
        {
            'subject': 'Objectif mensuel atteint',
            'message': 'Félicitations pour votre régularité',
            'data': {'type': 'goal', 'action': 'celebrate'}
        },
        {
            'subject': 'Nouveau cours disponible',
            'message': 'Stratégies d\'investissement avancées',
            'data': {'type': 'course', 'action': 'learn'}
        }
    ]
    
    # Créer des notifications pour tous les utilisateurs clients
    users = User.objects.filter(role='CUSTOMER', is_active=True)
    
    created_notifications = []
    for user in users:
        for notif_data in notifications_data:
            notification = create_notification(
                recipient=user,
                notification_type='IN_APP',
                subject=notif_data['subject'],
                message=notif_data['message'],
                data=notif_data['data'],
                priority='NORMAL'
            )
            created_notifications.append(notification)
    
    return created_notifications
