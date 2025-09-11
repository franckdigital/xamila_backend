# -*- coding: utf-8 -*-
"""
URLs pour l'interface Web Admin XAMILA
Back-office pour administrateurs et managers SGI
"""

from django.urls import path
from . import views_admin
from . import views_admin_advanced
from . import views_permissions

urlpatterns = [
    # ===== GESTION DES UTILISATEURS =====
    
    # Liste et statistiques des utilisateurs
    path('users/', views_admin.AdminUserListView.as_view(), name='admin_users_list'),
    path('users/<uuid:pk>/', views_admin.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('users/<uuid:user_id>/action/', views_admin.admin_user_action, name='admin_user_action'),
    
    # Role permission management endpoints
    path('role-permissions/', views_permissions.RolePermissionsManagementView.as_view(), name='admin_role_permissions'),
    path('toggle-role-permission/', views_permissions.toggle_role_permission, name='admin_toggle_role_permission'),
    path('permissions/update/', views_permissions.update_role_permission, name='admin_update_role_permission'),
    
    # User permissions endpoints
    path('permissions/', views_permissions.admin_permissions_list, name='admin_permissions'),
    path('permissions/roles/', views_permissions.admin_role_permissions_list, name='admin_role_permissions'),
    
    # CRUD utilisateurs
    path('users/create/', views_admin.admin_create_user, name='admin_create_user'),
    path('users/<uuid:user_id>/update/', views_admin.admin_update_user, name='admin_update_user'),
    path('users/<uuid:user_id>/delete/', views_admin.admin_delete_user, name='admin_delete_user'),
    path('users/<uuid:user_id>/toggle-status/', views_admin.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('users/<uuid:user_id>/toggle-payment/', views_admin.admin_toggle_user_payment, name='admin_toggle_user_payment'),
    path('users/<uuid:user_id>/toggle-certificate/', views_admin.admin_toggle_certificate, name='admin_toggle_certificate'),
    
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
    
    # ===== GESTION DES DÉFIS ÉPARGNE =====
    
    # Gestion des challenges épargne
    path('challenges/', views_admin.admin_challenges, name='admin_challenges'),
    path('challenges/<int:challenge_id>/', views_admin.admin_challenge_detail, name='admin_challenge_detail'),
    
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
