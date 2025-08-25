"""
URLs pour le module Notifications
Endpoints REST pour la gestion des notifications
"""

from django.urls import path
from . import views_notifications

app_name = 'notifications'

urlpatterns = [
    # === USER NOTIFICATIONS === (Essential endpoints only)
    path('user/notifications/', views_notifications.user_notifications, name='user-notifications'),
    path('user/count/', views_notifications.notification_count, name='notification-count'),
    path('<uuid:notification_id>/mark-read/', views_notifications.mark_notification_as_read, name='mark-as-read'),
    path('mark-all-read/', views_notifications.mark_all_notifications_as_read, name='mark-all-as-read'),
]
