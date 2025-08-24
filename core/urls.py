from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router pour les ViewSets (si nécessaire plus tard)
router = DefaultRouter()

urlpatterns = [
    # URLs du router
    path('', include(router.urls)),
    
    # === ENDPOINTS AUTHENTIFICATION ===
    path('auth/', include('core.urls_auth')),
    
    # === ENDPOINTS WEB ADMIN ===
    path('admin/', include('core.urls_admin')),
    
    # === ENDPOINTS BLOG ADMIN ===
    path('api/', include('core.urls_blog')),
    
    # === ENDPOINTS BLOG PUBLIC ===
    path('api/', include('core.urls_blog_public')),
    
    # === ENDPOINTS CUSTOMER ===
    path('customer/', include('core.urls_customer')),
    
    # === ENDPOINTS TRADING === (Temporairement désactivé - vues en cours de développement)
    # path('trading/', include('core.urls_trading')),
    
    # === ENDPOINTS LEARNING === (Temporairement désactivé - vues en cours de développement)
    # path('learning/', include('core.urls_learning')),
    
    # === ENDPOINTS NOTIFICATIONS === (Temporairement désactivé - vues en cours de développement)
    # path('notifications/', include('core.urls_notifications')),
    
    # === ENDPOINTS SAVINGS CHALLENGE === (Temporairement désactivé - vues en cours de développement)
    # path('savings/', include('core.urls_savings_challenge')),
    
    # === ENDPOINTS SGI ===
    
    # Liste et détails des SGI
    path('sgis/', views.SGIListView.as_view(), name='sgi-list'),
    path('sgis/<uuid:pk>/', views.SGIDetailView.as_view(), name='sgi-detail'),
    
    # === ENDPOINTS PROFIL CLIENT ===
    
    # Profil d'investissement du client
    path('profile/', views.ClientInvestmentProfileView.as_view(), name='client-profile'),
    path('profile/create/', views.ClientInvestmentProfileCreateView.as_view(), name='client-profile-create'),
    
    # === ENDPOINTS MATCHING SGI ===
    
    # Critères de matching disponibles
    path('matching/criteria/', views.matching_criteria_view, name='matching-criteria'),
    
    # Lancement du matching
    path('matching/launch/', views.SGIMatchingView.as_view(), name='sgi-matching'),
    
    # Résultats du matching
    path('matching/<uuid:pk>/results/', views.SGIMatchingResultsView.as_view(), name='matching-results'),
    
    # Sélection d'une SGI
    path('sgi/select/', views.SGISelectionView.as_view(), name='sgi-selection'),
    
    # === ENDPOINTS INTERACTIONS CLIENT ===
    
    # Interactions du client connecté
    path('interactions/', views.ClientInteractionsView.as_view(), name='client-interactions'),
    
    # === ENDPOINTS DASHBOARD ===
    # Dashboard URLs
    path('dashboard/', include('core.urls_dashboard')),
    
    # Savings URLs
    path('savings/', include('core.urls_savings')),
    
    # === ENDPOINTS ADMIN ===
    
    # Dashboard admin
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Statistiques SGI
    path('admin/statistics/sgis/', views.sgi_statistics_view, name='sgi-statistics'),
    
    # Statistiques clients
    path('admin/statistics/clients/', views.client_statistics_view, name='client-statistics'),
    
    # Notifications email
    path('admin/notifications/', views.EmailNotificationListView.as_view(), name='email-notifications'),
]
