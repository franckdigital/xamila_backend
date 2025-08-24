"""
URLs pour le module Notifications
Endpoints REST pour la gestion des notifications
"""

from django.urls import path
from . import views_notifications_basic as views_notifications

app_name = 'notifications'

urlpatterns = [
    # === NOTIFICATION TEMPLATES ===
    path('templates/', views_notifications.NotificationTemplateListView.as_view(), name='template-list'),
    path('templates/<uuid:pk>/', views_notifications.NotificationTemplateDetailView.as_view(), name='template-detail'),
    
    # === NOTIFICATION CAMPAIGNS ===
    path('campaigns/', views_notifications.NotificationCampaignListView.as_view(), name='campaign-list'),
    path('campaigns/<uuid:pk>/', views_notifications.NotificationCampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<uuid:campaign_id>/start/', views_notifications.start_campaign, name='start-campaign'),
    path('campaigns/<uuid:campaign_id>/pause/', views_notifications.pause_campaign, name='pause-campaign'),
    path('campaigns/<uuid:campaign_id>/analytics/', views_notifications.campaign_analytics, name='campaign-analytics'),
    
    # === NOTIFICATIONS ===
    path('', views_notifications.NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', views_notifications.NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:notification_id>/mark-read/', views_notifications.mark_as_read, name='mark-as-read'),
    path('mark-all-read/', views_notifications.mark_all_as_read, name='mark-all-as-read'),
    
    # === USER NOTIFICATIONS ===
    path('user/notifications/', views_notifications.user_notifications, name='user-notifications'),
    path('user/preferences/', views_notifications.NotificationPreferenceView.as_view(), name='user-preferences'),
    
    # === WEBHOOKS ===
    path('webhooks/', views_notifications.WebhookEndpointListView.as_view(), name='webhook-list'),
    path('webhooks/<uuid:pk>/', views_notifications.WebhookEndpointDetailView.as_view(), name='webhook-detail'),
    
    # === ANALYTICS ===
    path('stats/', views_notifications.notification_stats, name='notification-stats'),
]
