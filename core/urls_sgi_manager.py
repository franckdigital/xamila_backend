"""
URLs spécialisées pour les SGI_MANAGER
Routage des endpoints de gestion SGI
"""

from django.urls import path, include
from . import views_sgi_manager

app_name = 'sgi_manager'

urlpatterns = [
    # Profil du manager SGI
    path('profile/', views_sgi_manager.SGIManagerProfileView.as_view(), name='profile'),
    path('profile/create/', views_sgi_manager.SGIManagerProfileCreateView.as_view(), name='profile-create'),
    
    # Dashboard principal
    path('dashboard/', views_sgi_manager.SGIManagerDashboardView.as_view(), name='dashboard'),
    
    # Gestion des contrats
    path('contracts/', views_sgi_manager.ContractManagementView.as_view(), name='contracts'),
    path('contracts/approval/', views_sgi_manager.ContractApprovalView.as_view(), name='contract-approval'),
    
    # Gestion des clients
    path('clients/', views_sgi_manager.ClientManagementView.as_view(), name='clients'),
    
    # Métriques de performance
    path('performance/', views_sgi_manager.SGIPerformanceView.as_view(), name='performance'),
    
    # Gestion des alertes
    path('alerts/', views_sgi_manager.SGIAlertsView.as_view(), name='alerts'),
    path('alerts/<int:alert_id>/action/', views_sgi_manager.SGIAlertActionView.as_view(), name='alert-action'),
    
    # Analytics avancées
    path('analytics/', views_sgi_manager.SGIAnalyticsView.as_view(), name='analytics'),
    
    # Statistiques rapides
    path('statistics/', views_sgi_manager.sgi_manager_statistics, name='statistics'),
]
