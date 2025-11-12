from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_auth
from . import views_admin
from . import views_customer
from . import views_sgi_manager
from . import views_trading
from . import views_learning
from . import views_savings_goal
from . import views_notifications
from . import views, views_bilans, views_permissions, views_dashboard, views_blog, views_cohorte, views_ma_caisse
from .views_resources import get_resource_content
from .views_cohort_access import check_cohort_access, join_cohort_with_code, get_user_cohorts
from .views_cohorte import verifier_code_cohorte, mes_cohortes, activer_acces_challenge, creer_cohorte

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
    
    # === ENDPOINTS NOTIFICATIONS    # Notifications
    path('notifications/', include('core.urls_notifications')),
    
    # === ENDPOINTS RESOURCES ===
    path('resources/', get_resource_content, name='resources'),
    
    # === ENDPOINTS ADMIN RESOURCES ===
    path('admin/resources/', include('core.urls_admin_resources')),
    
    # User permissions
    path('user/permissions/', views_permissions.UserPermissionsView.as_view(), name='user_permissions'),
    path('user/permissions/check/<str:permission_code>/', views_permissions.check_permission, name='check_permission'),
    
    # === ENDPOINTS SAVINGS CHALLENGE === (Temporairement désactivé - vues en cours de développement)
    # path('savings/', include('core.urls_savings_challenge')),
    
    # === ENDPOINTS SGI ===
    
    # Liste et détails des SGI
    path('sgis/', views.SGIListView.as_view(), name='sgi-list'),
    path('sgis/<uuid:pk>/', views.SGIDetailView.as_view(), name='sgi-detail'),
    path('sgis/comparator/', views.SGIComparatorView.as_view(), name='sgi-comparator'),
    
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
    path('sgi/rating/', views.SGIRatingView.as_view(), name='sgi-rating'),
    
    # === ENDPOINTS INTERACTIONS CLIENT ===
    
    # Interactions du client connecté
    path('interactions/', views.ClientInteractionsView.as_view(), name='client-interactions'),

    # === ENDPOINTS OUVERTURE COMPTE TITRE ===
    path('account-opening/request/', views.AccountOpeningRequestCreateView.as_view(), name='account-opening-request-create'),
    path('account-opening/requests/', views.AccountOpeningRequestListView.as_view(), name='account-opening-requests'),
    path('account-opening/prefill/<uuid:sgi_id>/', views.ContractPrefillView.as_view(), name='contract-prefill'),
    path('account-opening/submit/', views.ContractSubmitOneClickView.as_view(), name='contract-submit-oneclick'),
    path('account-opening/authorize/', views.XamilaAuthorizationToggleView.as_view(), name='xamila-authorization-toggle'),
    path('account-opening/contract/pdf/', views.ContractPDFGenerateView.as_view(), name='contract-pdf-generate'),
    
    # === ENDPOINTS DASHBOARD ===
    # Dashboard URLs
    path('dashboard/', include('core.urls_dashboard')),
    
    # Bilans financiers URLs
    path('bilans/', include('core.urls_bilans')),
    
    # Savings URLs
    path('savings/', include('core.urls_savings')),
    
    # Savings Goal URLs
    path('savings-goal/', include('core.urls_savings_goal')),
    
    # === ENDPOINTS COHORT ACCESS ===
    
    # Vérification accès cohorte
    path('user/cohort-access/', check_cohort_access, name='check-cohort-access'),
    
    # Adhésion à une cohorte via code
    path('user/join-cohort/', join_cohort_with_code, name='join-cohort-with-code'),
    
    # Cohortes de l'utilisateur
    path('user/cohorts/', get_user_cohorts, name='get-user-cohorts'),
    
    # === ENDPOINTS ADMIN ===
    
    # Dashboard admin
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Statistiques SGI
    path('admin/statistics/sgis/', views.sgi_statistics_view, name='sgi-statistics'),
    
    # Statistiques clients
    path('admin/statistics/clients/', views.client_statistics_view, name='client-statistics'),
    
    # Notifications email
    path('admin/notifications/', views.EmailNotificationListView.as_view(), name='email-notifications'),
    
    # === ENDPOINTS COHORTES ===
    path('cohortes/verifier-code/', views_cohorte.verifier_code_cohorte, name='verifier_code_cohorte'),
    path('cohortes/mes-cohortes/', views_cohorte.mes_cohortes, name='mes_cohortes'),
    path('cohortes/activer-acces/', views_cohorte.activer_acces_challenge, name='activer_acces_challenge'),
    path('cohortes/creer/', views_cohorte.creer_cohorte, name='creer_cohorte'),
    
    # Ma Caisse endpoints
    path('ma-caisse/verifier-activation/', views_ma_caisse.verifier_activation_caisse, name='verifier_activation_caisse'),
    path('ma-caisse/statut-objectifs/', views_ma_caisse.statut_objectifs_epargne, name='statut_objectifs_epargne'),
]
