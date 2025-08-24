from django.urls import path
from . import views_auth

urlpatterns = [
    # ================================
    # ENREGISTREMENT PAR RÔLES
    # ================================
    
    # Enregistrement clients/épargnants (public)
    path('register/customer/', views_auth.register_customer, name='register_customer'),
    
    # Enregistrement étudiants/apprenants (public)
    path('register/student/', views_auth.register_student, name='register_student'),
    
    # Enregistrement managers SGI (public)
    path('register/sgi-manager/', views_auth.register_sgi_manager, name='register_sgi_manager'),
    
    # Enregistrement instructeurs/formateurs (public)
    path('register/instructor/', views_auth.register_instructor, name='register_instructor'),
    
    # Enregistrement support client (public)
    path('register/support/', views_auth.register_support, name='register_support'),
    
    # Enregistrement administrateur (public - avec vérification renforcée)
    path('register/admin/', views_auth.register_admin, name='register_admin'),
    
    # ================================
    # GESTION ADMIN DES UTILISATEURS
    # ================================
    
    # Création d'utilisateurs par l'admin (admin seulement)
    path('admin/users/create/', views_auth.AdminUserCreateView.as_view(), name='admin_create_user'),
    
    # Liste de tous les utilisateurs (admin seulement)
    path('admin/users/', views_auth.AdminUserListView.as_view(), name='admin_list_users'),
    
    # ================================
    # VÉRIFICATION ET ACTIVATION
    # ================================
    
    # Vérification du code OTP
    path('verify-otp/', views_auth.verify_otp, name='verify_otp'),
    
    # Renvoyer un code OTP
    path('resend-otp/', views_auth.resend_otp, name='resend_otp'),
    
    # ================================
    # CONNEXION ET PROFIL
    # ================================
    
    # Connexion utilisateur
    path('login/', views_auth.login_user, name='login_user'),
    
    # Profil utilisateur connecté
    path('profile/', views_auth.user_profile, name='user_profile'),
    
    # Mise à jour du profil
    path('profile/update/', views_auth.update_user_profile, name='update_user_profile'),
    
    # ================================
    # GESTION DES MOTS DE PASSE
    # ================================
    
    # Changer le mot de passe (utilisateur connecté)
    path('change-password/', views_auth.change_password, name='change_password'),
    
    # Demander la réinitialisation du mot de passe
    path('forgot-password/', views_auth.forgot_password, name='forgot_password'),
    
    # Réinitialiser le mot de passe avec token
    path('reset-password/', views_auth.reset_password, name='reset_password'),
]
