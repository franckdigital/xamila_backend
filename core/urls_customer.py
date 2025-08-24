"""
URLs pour les fonctionnalités CUSTOMER (clients)
Authentification, KYC, gestion de profil
"""

from django.urls import path, include
from . import views_customer

app_name = 'customer'

urlpatterns = [
    # === AUTHENTIFICATION CUSTOMER ===
    
    # Inscription
    path('auth/register/', views_customer.CustomerRegistrationView.as_view(), name='register'),
    
    # Vérification OTP
    path('auth/verify-otp/', views_customer.CustomerOTPVerificationView.as_view(), name='verify_otp'),
    
    # Renvoyer OTP
    path('auth/resend-otp/', views_customer.resend_otp, name='resend_otp'),
    
    # Connexion
    path('auth/login/', views_customer.CustomerLoginView.as_view(), name='login'),
    
    # === GESTION PROFIL KYC ===
    
    # Créer profil KYC
    path('kyc/profile/create/', views_customer.KYCProfileCreateView.as_view(), name='kyc_profile_create'),
    
    # Récupérer/Modifier profil KYC
    path('kyc/profile/', views_customer.KYCProfileView.as_view(), name='kyc_profile'),
    
    # Statut KYC détaillé
    path('kyc/status/', views_customer.KYCStatusView.as_view(), name='kyc_status'),
    
    # Soumettre profil pour révision
    path('kyc/submit/', views_customer.KYCSubmitForReviewView.as_view(), name='kyc_submit'),
    
    # === GESTION DOCUMENTS KYC ===
    
    # Upload document
    path('kyc/documents/upload/', views_customer.KYCDocumentUploadView.as_view(), name='kyc_document_upload'),
    
    # Liste des documents
    path('kyc/documents/', views_customer.KYCDocumentListView.as_view(), name='kyc_document_list'),
]
