# -*- coding: utf-8 -*-
"""
URLs pour l'interface Web Admin XAMILA
Back-office pour administrateurs et managers SGI
"""

from django.urls import path
from . import views_admin
from . import views_admin_advanced

urlpatterns = [
    # ===== GESTION DES UTILISATEURS =====
    
    # Liste et statistiques des utilisateurs
    path('users/', views_admin.AdminUserListView.as_view(), name='admin_users_list'),
    path('users/<uuid:pk>/', views_admin.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('users/<uuid:user_id>/action/', views_admin.admin_user_action, name='admin_user_action'),
    
    # ===== TABLEAU DE BORD ADMIN =====
    
    # Statistiques générales du dashboard
    path('dashboard/stats/', views_admin.admin_dashboard_stats, name='admin_dashboard_stats'),
    
    # ===== GESTION DES SGI =====
    
    # Liste et gestion des SGI
    path('sgis/', views_admin.admin_sgi_list, name='admin_sgi_list'),
    path('sgis/<uuid:sgi_id>/action/', views_admin.admin_sgi_action, name='admin_sgi_action'),
    
    # ===== GESTION DU CONTENU E-LEARNING =====
    
    # Statistiques du contenu
    path('content/stats/', views_admin.admin_content_stats, name='admin_content_stats'),
    
    # ===== LOGS ET AUDIT =====
    
    # Logs d'activité
    path('logs/', views_admin.admin_activity_logs, name='admin_activity_logs'),
    
    # ===== FONCTIONNALITÉS AVANCÉES =====
    
    # Analytics SGI avancées
    path('sgis/analytics/', views_admin_advanced.admin_sgi_analytics, name='admin_sgi_analytics'),
    path('sgis/bulk-action/', views_admin_advanced.admin_sgi_bulk_action, name='admin_sgi_bulk_action'),
    
    # Gestion avancée des contrats
    path('contracts/', views_admin_advanced.admin_contracts_list, name='admin_contracts_list'),
    path('contracts/dashboard/', views_admin_advanced.admin_contracts_dashboard, name='admin_contracts_dashboard'),
    path('contracts/<uuid:contract_id>/action/', views_admin_advanced.admin_contract_action, name='admin_contract_action'),
    
    # Reporting et exports
    path('export/users/', views_admin_advanced.admin_export_users, name='admin_export_users'),
    path('bi/', views_admin_advanced.admin_business_intelligence, name='admin_business_intelligence'),
    
    # Système de matching
    path('matching/analytics/', views_admin_advanced.admin_matching_analytics, name='admin_matching_analytics'),
    path('matching/configure/', views_admin_advanced.admin_configure_matching, name='admin_configure_matching'),
]
