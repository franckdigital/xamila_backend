"""
Vues d'authentification et de gestion pour les utilisateurs CUSTOMER
Inclut la gestion complète du KYC (Know Your Customer)
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import random
import string
from datetime import timedelta

from .models import OTP
from .models_kyc import KYCProfile, KYCDocument, KYCVerificationLog
from .serializers_kyc import (
    KYCProfileSerializer, KYCProfileCreateSerializer, KYCProfileUpdateSerializer,
    KYCDocumentSerializer, DocumentUploadSerializer, KYCVerificationLogSerializer,
    KYCDashboardSerializer
)
from .serializers_auth import (
    CustomerRegistrationSerializer, CustomerRegistrationResponseSerializer,
    OTPVerificationSerializer, OTPVerificationResponseSerializer,
    CustomerLoginSerializer, CustomerLoginResponseSerializer,
    ResendOTPSerializer, ResendOTPResponseSerializer,
    ErrorResponseSerializer
)
from .utils_sms import send_sms_otp
from .utils_email import send_email_otp
from .utils_kyc import KYCVerificationService

User = get_user_model()


@extend_schema(
    tags=['Authentication'],
    summary='Inscription client',
    description='Inscription d\'un nouveau client sur la plateforme Xamila avec envoi automatique des codes OTP.',
    request=CustomerRegistrationSerializer,
    responses={
        201: CustomerRegistrationResponseSerializer,
        400: ErrorResponseSerializer
    }
)
class CustomerRegistrationView(CreateAPIView):
    """
    Inscription d'un nouveau client CUSTOMER
    Étape 1: Création du compte avec vérification OTP
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Validation des données de base
        required_fields = ['email', 'password', 'phone', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'error': f'Le champ {field} est obligatoire.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        email = data.get('email').lower().strip()
        phone = data.get('phone').strip()
        password = data.get('password')
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Un compte avec cet email existe déjà.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone=phone).exists():
            return Response({
                'error': 'Un compte avec ce numéro de téléphone existe déjà.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider le mot de passe
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({
                'error': 'Mot de passe invalide.',
                'details': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=email,  # Utiliser l'email comme username
                    email=email,
                    password=password,
                    phone=phone,
                    first_name=first_name,
                    last_name=last_name,
                    role='CUSTOMER',
                    is_active=False  # Désactivé jusqu'à vérification OTP
                )
                
                # Générer et envoyer les OTP
                email_otp = self.generate_and_send_otp(user, 'EMAIL_VERIFICATION', 'email')
                sms_otp = self.generate_and_send_otp(user, 'PHONE_VERIFICATION', 'sms')
                
                return Response({
                    'message': 'Compte créé avec succès. Vérifiez votre email et SMS pour les codes OTP.',
                    'user_id': str(user.id),
                    'email': user.email,
                    'phone': user.phone,
                    'next_step': 'verify_otp'
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la création du compte.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def generate_and_send_otp(self, user, otp_type, method):
        """Génère et envoie un code OTP"""
        # Supprimer les anciens OTP non utilisés
        OTP.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).delete()
        
        # Générer un nouveau code OTP
        code = ''.join(random.choices(string.digits, k=6))
        
        # Créer l'OTP en base
        otp = OTP.objects.create(
            user=user,
            code=code,
            otp_type=otp_type,
            expires_at=timezone.now() + timedelta(minutes=10)  # Expire dans 10 minutes
        )
        
        # Envoyer l'OTP
        if method == 'email':
            send_email_otp(user.email, code, user.first_name)
        elif method == 'sms':
            send_sms_otp(user.phone, code)
        
        return otp


@extend_schema(
    tags=['Authentication'],
    summary='Vérification OTP',
    description='Vérification des codes OTP (email + SMS) pour activer le compte client.',
    request=OTPVerificationSerializer,
    responses={
        200: OTPVerificationResponseSerializer,
        400: ErrorResponseSerializer
    }
)
class CustomerOTPVerificationView(APIView):
    """
    Vérification des codes OTP pour l'activation du compte
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        data = request.data
        
        user_id = data.get('user_id')
        email_otp = data.get('email_otp')
        sms_otp = data.get('sms_otp')
        
        if not all([user_id, email_otp, sms_otp]):
            return Response({
                'error': 'user_id, email_otp et sms_otp sont obligatoires.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id, role='CUSTOMER')
        except User.DoesNotExist:
            return Response({
                'error': 'Utilisateur non trouvé.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier les OTP
        email_valid = self.verify_otp(user, email_otp, 'EMAIL_VERIFICATION')
        sms_valid = self.verify_otp(user, sms_otp, 'PHONE_VERIFICATION')
        
        if not email_valid:
            return Response({
                'error': 'Code OTP email invalide ou expiré.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not sms_valid:
            return Response({
                'error': 'Code OTP SMS invalide ou expiré.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Activer le compte
        with transaction.atomic():
            user.is_active = True
            user.email_verified = True
            user.phone_verified = True
            user.save()
            
            # Marquer les OTP comme utilisés
            OTP.objects.filter(
                user=user,
                otp_type__in=['EMAIL_VERIFICATION', 'PHONE_VERIFICATION'],
                is_used=False
            ).update(is_used=True)
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Compte activé avec succès.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_verified': user.is_verified
            },
            'next_step': 'complete_kyc'
        }, status=status.HTTP_200_OK)
    
    def verify_otp(self, user, code, otp_type):
        """Vérifie un code OTP"""
        try:
            otp = OTP.objects.get(
                user=user,
                code=code,
                otp_type=otp_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            return True
        except OTP.DoesNotExist:
            return False


@extend_schema(
    tags=['Authentication'],
    summary='Connexion client',
    description='Connexion sécurisée pour les clients avec retour des tokens JWT et informations KYC.',
    request=CustomerLoginSerializer,
    responses={
        200: CustomerLoginResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
)
class CustomerLoginView(TokenObtainPairView):
    """
    Connexion sécurisée pour les clients CUSTOMER
    """
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe obligatoires.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authentifier l'utilisateur
        user = authenticate(username=email, password=password)
        
        if not user:
            return Response({
                'error': 'Identifiants invalides.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role != 'CUSTOMER':
            return Response({
                'error': 'Accès non autorisé pour ce type de compte.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not user.is_active:
            return Response({
                'error': 'Compte non activé. Vérifiez vos emails/SMS pour les codes OTP.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Générer les tokens
        refresh = RefreshToken.for_user(user)
        
        # Vérifier le statut KYC
        kyc_status = 'not_started'
        kyc_completion = 0
        
        try:
            kyc_profile = user.kyc_profile
            kyc_status = kyc_profile.kyc_status.lower()
            kyc_completion = kyc_profile.completion_percentage
        except KYCProfile.DoesNotExist:
            pass
        
        return Response({
            'message': 'Connexion réussie.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_verified': user.is_verified,
                'kyc_status': kyc_status,
                'kyc_completion': kyc_completion
            }
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['KYC'],
    summary='Créer profil KYC',
    description='Création du profil KYC complet pour un client authentifié (informations personnelles, adresse, documents d\'identité).',
    request=KYCProfileCreateSerializer,
    responses={
        201: KYCProfileSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
)
class KYCProfileCreateView(CreateAPIView):
    """
    Création du profil KYC pour un client
    """
    serializer_class = KYCProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Vérifier que l'utilisateur est un CUSTOMER
        if self.request.user.role != 'CUSTOMER':
            raise permissions.PermissionDenied("Seuls les clients peuvent créer un profil KYC.")
        
        # Vérifier qu'il n'a pas déjà un profil KYC
        if hasattr(self.request.user, 'kyc_profile'):
            raise ValidationError("Un profil KYC existe déjà pour cet utilisateur.")
        
        # Créer le profil
        kyc_profile = serializer.save(user=self.request.user)
        
        # Log de création
        KYCVerificationLog.objects.create(
            kyc_profile=kyc_profile,
            action_type='PROFILE_CREATED',
            description=f"Profil KYC créé pour {kyc_profile.full_name}",
            performed_by=self.request.user,
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Récupère l'IP du client"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class KYCProfileView(RetrieveUpdateAPIView):
    """
    Récupération et mise à jour du profil KYC
    """
    serializer_class = KYCProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Récupérer le profil KYC de l'utilisateur connecté
        try:
            return self.request.user.kyc_profile
        except KYCProfile.DoesNotExist:
            return None
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return KYCProfileUpdateSerializer
        return KYCProfileSerializer
    
    def update(self, request, *args, **kwargs):
        kyc_profile = self.get_object()
        
        if not kyc_profile:
            return Response({
                'error': 'Aucun profil KYC trouvé. Créez d\'abord votre profil.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Log de mise à jour
        old_values = {
            'first_name': kyc_profile.first_name,
            'last_name': kyc_profile.last_name,
            'kyc_status': kyc_profile.kyc_status
        }
        
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            KYCVerificationLog.objects.create(
                kyc_profile=kyc_profile,
                action_type='PROFILE_UPDATED',
                description=f"Profil KYC mis à jour pour {kyc_profile.full_name}",
                performed_by=request.user,
                ip_address=self.get_client_ip(),
                old_values=old_values,
                new_values=request.data
            )
        
        return response
    
    def get_client_ip(self):
        """Récupère l'IP du client"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class KYCDocumentUploadView(APIView):
    """
    Upload de documents KYC
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Vérifier que l'utilisateur a un profil KYC
        try:
            kyc_profile = request.user.kyc_profile
        except KYCProfile.DoesNotExist:
            return Response({
                'error': 'Aucun profil KYC trouvé. Créez d\'abord votre profil.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que le profil peut être modifié
        if kyc_profile.kyc_status in ['APPROVED', 'UNDER_REVIEW']:
            return Response({
                'error': 'Impossible de téléverser des documents pour un profil approuvé ou en cours de révision.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DocumentUploadSerializer(
            data=request.data,
            context={'kyc_profile': kyc_profile}
        )
        
        if serializer.is_valid():
            document = serializer.save()
            
            # Log d'upload
            KYCVerificationLog.objects.create(
                kyc_profile=kyc_profile,
                action_type='DOCUMENT_UPLOADED',
                description=f"Document téléversé: {document.get_document_type_display()}",
                performed_by=request.user,
                ip_address=self.get_client_ip()
            )
            
            # Déclencher la vérification automatique si configurée
            if getattr(settings, 'KYC_AUTO_VERIFICATION_ENABLED', False):
                self.trigger_auto_verification(document)
            
            return Response(
                KYCDocumentSerializer(document, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def trigger_auto_verification(self, document):
        """Déclenche la vérification automatique du document"""
        try:
            verification_service = KYCVerificationService()
            verification_service.verify_document(document)
        except Exception as e:
            # Log l'erreur mais ne pas faire échouer l'upload
            print(f"Erreur lors de la vérification automatique: {e}")
    
    def get_client_ip(self):
        """Récupère l'IP du client"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class KYCDocumentListView(ListAPIView):
    """
    Liste des documents KYC de l'utilisateur
    """
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            kyc_profile = self.request.user.kyc_profile
            return KYCDocument.objects.filter(kyc_profile=kyc_profile)
        except KYCProfile.DoesNotExist:
            return KYCDocument.objects.none()


class KYCSubmitForReviewView(APIView):
    """
    Soumission du profil KYC pour révision
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            kyc_profile = request.user.kyc_profile
        except KYCProfile.DoesNotExist:
            return Response({
                'error': 'Aucun profil KYC trouvé.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que le profil peut être soumis
        if kyc_profile.kyc_status != 'PENDING':
            return Response({
                'error': f'Impossible de soumettre un profil avec le statut: {kyc_profile.get_kyc_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que les documents obligatoires sont présents
        required_docs = ['IDENTITY_FRONT', 'SELFIE', 'PROOF_OF_ADDRESS']
        uploaded_docs = kyc_profile.documents.values_list('document_type', flat=True)
        
        missing_docs = [doc for doc in required_docs if doc not in uploaded_docs]
        if missing_docs:
            doc_names = [dict(KYCDocument.DOCUMENT_TYPES)[doc] for doc in missing_docs]
            return Response({
                'error': 'Documents manquants pour la soumission.',
                'missing_documents': doc_names
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Soumettre pour révision
        kyc_profile.submit_for_review()
        
        # Log de soumission
        KYCVerificationLog.objects.create(
            kyc_profile=kyc_profile,
            action_type='PROFILE_SUBMITTED',
            description=f"Profil KYC soumis pour révision: {kyc_profile.full_name}",
            performed_by=request.user,
            ip_address=self.get_client_ip()
        )
        
        return Response({
            'message': 'Profil KYC soumis pour révision avec succès.',
            'status': kyc_profile.kyc_status,
            'submitted_at': kyc_profile.submitted_at
        }, status=status.HTTP_200_OK)
    
    def get_client_ip(self):
        """Récupère l'IP du client"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class KYCStatusView(APIView):
    """
    Récupération du statut KYC détaillé
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            kyc_profile = request.user.kyc_profile
            serializer = KYCProfileSerializer(kyc_profile, context={'request': request})
            
            return Response({
                'kyc_profile': serializer.data,
                'required_documents': [
                    {'type': 'IDENTITY_FRONT', 'name': 'Pièce d\'identité (recto)', 'required': True},
                    {'type': 'IDENTITY_BACK', 'name': 'Pièce d\'identité (verso)', 'required': False},
                    {'type': 'SELFIE', 'name': 'Photo selfie', 'required': True},
                    {'type': 'PROOF_OF_ADDRESS', 'name': 'Justificatif de domicile', 'required': True},
                ],
                'next_steps': self.get_next_steps(kyc_profile)
            }, status=status.HTTP_200_OK)
            
        except KYCProfile.DoesNotExist:
            return Response({
                'message': 'Aucun profil KYC trouvé.',
                'next_steps': ['Créer votre profil KYC']
            }, status=status.HTTP_404_NOT_FOUND)
    
    def get_next_steps(self, kyc_profile):
        """Détermine les prochaines étapes pour l'utilisateur"""
        if kyc_profile.kyc_status == 'PENDING':
            steps = []
            
            # Vérifier les champs manquants
            if not all([kyc_profile.first_name, kyc_profile.last_name, 
                       kyc_profile.date_of_birth, kyc_profile.address_line_1]):
                steps.append('Compléter les informations personnelles')
            
            # Vérifier les documents manquants
            required_docs = ['IDENTITY_FRONT', 'SELFIE', 'PROOF_OF_ADDRESS']
            uploaded_docs = kyc_profile.documents.values_list('document_type', flat=True)
            missing_docs = [doc for doc in required_docs if doc not in uploaded_docs]
            
            if missing_docs:
                steps.append('Téléverser les documents manquants')
            
            if not steps:
                steps.append('Soumettre le profil pour révision')
            
            return steps
            
        elif kyc_profile.kyc_status == 'UNDER_REVIEW':
            return ['Attendre la révision par notre équipe']
            
        elif kyc_profile.kyc_status == 'APPROVED':
            return ['Profil KYC approuvé - Vous pouvez utiliser tous les services']
            
        elif kyc_profile.kyc_status == 'REJECTED':
            return ['Corriger les informations selon les commentaires et soumettre à nouveau']
            
        return []


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_otp(request):
    """
    Renvoie un code OTP
    """
    user_id = request.data.get('user_id')
    otp_type = request.data.get('otp_type')  # 'email' ou 'sms'
    
    if not user_id or not otp_type:
        return Response({
            'error': 'user_id et otp_type sont obligatoires.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Générer et envoyer le nouvel OTP
    registration_view = CustomerRegistrationView()
    
    if otp_type == 'email':
        registration_view.generate_and_send_otp(user, 'EMAIL_VERIFICATION', 'email')
        message = 'Code OTP envoyé par email.'
    elif otp_type == 'sms':
        registration_view.generate_and_send_otp(user, 'PHONE_VERIFICATION', 'sms')
        message = 'Code OTP envoyé par SMS.'
    else:
        return Response({
            'error': 'Type OTP invalide. Utilisez "email" ou "sms".'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': message
    }, status=status.HTTP_200_OK)
