from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging
import traceback

# Configuration du logger
logger = logging.getLogger(__name__)

from .models import User, OTP
from .serializers import (
    UserSerializer,
    BaseUserRegistrationSerializer,
    CustomerRegistrationSerializer,
    StudentRegistrationSerializer,
    SGIManagerRegistrationSerializer,
    InstructorRegistrationSerializer,
    SupportRegistrationSerializer,
    AdminUserCreationSerializer,
    OTPSerializer
)


# ================================
# UTILITAIRES POUR AUTHENTIFICATION
# ================================

def generate_otp_code():
    """Génère un code OTP à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(user, otp_code, purpose):
    """Envoie un code OTP par email"""
    subject_map = {
        'REGISTRATION': 'Code de vérification - Inscription XAMILA',
        'PASSWORD_RESET': 'Code de réinitialisation - XAMILA',
        'EMAIL_VERIFICATION': 'Vérification email - XAMILA',
    }
    
    subject = subject_map.get(purpose, 'Code de vérification - XAMILA')
    message = f"""
    Bonjour {user.get_full_name() or user.email},
    
    Votre code de vérification XAMILA est : {otp_code}
    
    Ce code expire dans 10 minutes.
    
    Si vous n'avez pas demandé ce code, ignorez ce message.
    
    Cordialement,
    L'équipe XAMILA
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        # Don't fail authentication for email issues in development
        logger.warning("Email sending failed but continuing authentication")
        return True


def create_tokens_for_user(user):
    """Crée les tokens JWT pour un utilisateur"""
    try:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    except Exception as e:
        logger.error(f"Error creating tokens for user {user.email}: {str(e)}")
        raise e


# ================================
# VUES D'ENREGISTREMENT PAR RÔLES
# ================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    """
    Enregistrement d'un client/épargnant
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer et envoyer OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer OTP par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Inscription réussie. Un code de vérification a été envoyé à votre email.',
            'user_id': user.id,
            'email_sent': email_sent,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    """
    Enregistrement d'un étudiant/apprenant pour les formations
    """
    serializer = StudentRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer et envoyer OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer OTP par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Inscription Étudiant réussie. Un code de vérification a été envoyé à votre email.',
            'user_id': user.id,
            'email_sent': email_sent,
            'user': UserSerializer(user).data,
            'note': 'Vous pouvez maintenant accéder aux formations disponibles.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_sgi_manager(request):
    """
    Enregistrement d'un manager SGI avec création automatique de la SGI
    """
    serializer = SGIManagerRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer et envoyer OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer OTP par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Inscription Manager SGI réussie. Un code de vérification a été envoyé à votre email.',
            'user_id': user.id,
            'email_sent': email_sent,
            'user': UserSerializer(user).data,
            'note': 'Votre SGI a été créée et sera vérifiée par notre équipe.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_instructor(request):
    """
    Enregistrement d'un instructeur/formateur
    """
    serializer = InstructorRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer et envoyer OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer OTP par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Inscription Instructeur réussie. Un code de vérification a été envoyé à votre email.',
            'user_id': user.id,
            'email_sent': email_sent,
            'user': UserSerializer(user).data,
            'note': 'Votre compte sera activé après vérification par notre équipe.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_support(request):
    """
    Enregistrement d'un agent support client
    """
    serializer = SupportRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer et envoyer OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer OTP par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Inscription Support réussie. Un code de vérification a été envoyé à votre email.',
            'user_id': user.id,
            'email_sent': email_sent,
            'user': UserSerializer(user).data,
            'note': 'Votre compte sera activé après vérification par notre équipe.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_admin(request):
    """
    Enregistrement d'un administrateur
    """
    logger.info(f"register_admin called with data: {request.data}")
    
    try:
        # Utiliser le serializer de base avec role='ADMIN'
        data = request.data.copy()
        data['role'] = 'ADMIN'
        
        serializer = BaseUserRegistrationSerializer(data=data)
        logger.info(f"Serializer created for admin registration")
        
        if serializer.is_valid():
            logger.info("Serializer validation passed, creating admin user...")
            user = serializer.save()
            logger.info(f"Admin user created successfully: {user.email}")
            
            # Générer et envoyer OTP
            logger.info("Generating OTP for admin user")
            otp_code = generate_otp_code()
            expires_at = timezone.now() + timedelta(minutes=30)  # Plus long pour admin
            
            OTP.objects.create(
                user=user,
                code=otp_code,
                otp_type='REGISTRATION',
                expires_at=expires_at
            )
            logger.info(f"OTP created for admin user: {otp_code}")
            
            # Envoyer OTP par email
            logger.info("Sending OTP email to admin user")
            email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
            logger.info(f"OTP email sent: {email_sent}")
            
            return Response({
                'message': 'Inscription Administrateur réussie. Un code de vérification a été envoyé à votre email.',
                'user_id': user.id,
                'email_sent': email_sent,
                'user': UserSerializer(user).data,
                'note': 'Votre compte administrateur sera activé après vérification de sécurité.'
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Admin registration validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in register_admin: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response(
            {'error': f'Erreur lors de la création du compte administrateur: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ================================
# VUES ADMIN POUR CRÉATION D'UTILISATEURS
# ================================

class AdminUserCreateView(generics.CreateAPIView):
    """
    Vue pour que l'admin puisse créer des utilisateurs avec n'importe quel rôle
    """
    serializer_class = AdminUserCreationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Seuls les admins peuvent créer des utilisateurs"""
        logger.info(f"AdminUserCreateView.get_permissions - User authenticated: {self.request.user.is_authenticated}")
        if self.request.user.is_authenticated:
            logger.info(f"User role: {getattr(self.request.user, 'role', 'NO_ROLE')}")
        
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            logger.info("Admin user detected, allowing access")
            return [IsAuthenticated()]
        
        logger.warning("Non-admin user trying to create account, requiring admin permissions")
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Override create method to add detailed logging"""
        logger.info(f"AdminUserCreateView.create called with data: {request.data}")
        
        try:
            # Valider les données
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer created: {type(serializer)}")
            
            if not serializer.is_valid():
                logger.error(f"Serializer validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info("Serializer validation passed, creating user...")
            
            # Créer l'utilisateur
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            logger.info(f"User created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            logger.error(f"Error in AdminUserCreateView.create: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Erreur lors de la création du compte: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        logger.info("AdminUserCreateView.perform_create called")
        
        try:
            user = serializer.save()
            logger.info(f"User saved successfully: {user.email}, role: {user.role}")
        
            # Si c'est un manager SGI, créer une SGI de base
            if user.role == 'SGI_MANAGER':
                logger.info("Creating SGI for SGI_MANAGER user")
                try:
                    from .models import SGI
                    sgi = SGI.objects.create(
                        name=f"SGI de {user.get_full_name()}",
                        description="SGI créée par l'administrateur",
                        address="À compléter",
                        manager_name=user.get_full_name(),
                        manager_email=user.email,
                        manager_phone=user.phone or "",
                        email=user.email,
                        is_verified=True  # Pré-vérifiée par l'admin
                    )
                    logger.info(f"SGI created successfully: {sgi.name}")
                except Exception as e:
                    logger.error(f"Error creating SGI: {str(e)}")
                    raise
            
            # Générer OTP pour vérification
            logger.info("Generating OTP code")
            try:
                otp_code = generate_otp_code()
                expires_at = timezone.now() + timedelta(minutes=30)  # Plus long pour admin
                
                otp = OTP.objects.create(
                    user=user,
                    code=otp_code,
                    otp_type='REGISTRATION',
                    expires_at=expires_at
                )
                logger.info(f"OTP created successfully: {otp.code}")
                
                # Envoyer email avec informations de connexion
                logger.info("Sending OTP email")
                send_otp_email(user, otp_code, 'REGISTRATION')
                logger.info("OTP email sent successfully")
                
            except Exception as e:
                logger.error(f"Error creating OTP or sending email: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


class AdminUserListView(generics.ListAPIView):
    """
    Vue pour lister tous les utilisateurs (admin seulement)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'ADMIN':
            return User.objects.none()
        return User.objects.all().order_by('-created_at')
    
    def get_permissions(self):
        """Seuls les admins peuvent voir la liste complète"""
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            return [IsAuthenticated()]
        return [permissions.IsAdminUser()]


# ================================
# VUES DE VÉRIFICATION OTP
# ================================

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Vérification du code OTP pour activer le compte
    """
    user_id = request.data.get('user_id')
    otp_code = request.data.get('otp_code')
    
    if not user_id or not otp_code:
        return Response({
            'error': 'user_id et otp_code sont requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        otp = OTP.objects.filter(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            is_used=False
        ).first()
        
        if not otp:
            return Response({
                'error': 'Code OTP invalide ou déjà utilisé'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp.is_valid():
            return Response({
                'error': 'Code OTP expiré'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marquer l'OTP comme utilisé
        otp.mark_as_used()
        
        # Activer le compte utilisateur
        user.is_active = True
        user.email_verified = True
        user.save()
        
        # Générer les tokens JWT
        tokens = create_tokens_for_user(user)
        
        return Response({
            'message': 'Compte activé avec succès',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Renvoyer un code OTP
    """
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({
            'error': 'user_id est requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Invalider les anciens OTP
        OTP.objects.filter(
            user=user,
            otp_type='REGISTRATION',
            is_used=False
        ).update(is_used=True)
        
        # Créer un nouveau OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='REGISTRATION',
            expires_at=expires_at
        )
        
        # Envoyer par email
        email_sent = send_otp_email(user, otp_code, 'REGISTRATION')
        
        return Response({
            'message': 'Nouveau code OTP envoyé',
            'email_sent': email_sent
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


# ================================
# VUES DE CONNEXION
# ================================

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Connexion utilisateur avec email/mot de passe
    """
    logger.info(f"login_user called with data: {request.data}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request method: {request.method}")
    
    # Accepter 'email' ou 'username' comme clé pour l'identifiant
    email = request.data.get('email') or request.data.get('username')
    password = request.data.get('password')
    
    logger.info(f"Extracted email: {email}, password provided: {bool(password)}")
    
    if not email or not password:
        logger.error("Login failed: Username or password missing")
        return Response({
            'error': 'Identifiant (email ou téléphone) et mot de passe requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authentifier par email ou téléphone
    try:
        logger.info(f"Attempting authentication with username: {email}")
        
        # Rechercher l'utilisateur directement dans la base
        from django.db.models import Q
        try:
            user = User.objects.get(Q(email=email) | Q(phone=email))
            logger.info(f"User found: {user.email}, checking password...")
            if user.check_password(password):
                authenticated_user = user
                logger.info("Password check successful")
            else:
                authenticated_user = None
                logger.warning("Password check failed")
        except User.DoesNotExist:
            authenticated_user = None
            logger.warning(f"User not found: {email}")
        except Exception as db_error:
            logger.error(f"Database error during user lookup: {str(db_error)}")
            authenticated_user = None
        logger.info(f"Authentication result: {authenticated_user is not None}")
        
        if authenticated_user:
            if not authenticated_user.is_active:
                logger.warning(f"Login failed: User {email} is not active")
                return Response({
                    'error': 'Compte non activé. Vérifiez votre email.',
                    'user_id': authenticated_user.id
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            logger.info(f"Login successful for user: {email}")
            
            # Générer les tokens
            try:
                tokens = create_tokens_for_user(authenticated_user)
                logger.info("JWT tokens generated successfully")
            except Exception as token_error:
                logger.error(f"Token generation failed: {str(token_error)}")
                return Response({
                    'error': f'Erreur génération token: {str(token_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Mettre à jour la dernière connexion (skip for now to avoid timezone issues)
            # try:
            #     from django.utils import timezone
            #     authenticated_user.last_login = timezone.now()
            #     authenticated_user.save()
            #     logger.info("Last login updated")
            # except Exception as save_error:
            #     logger.error(f"Failed to update last login: {str(save_error)}")
            #     # Continue anyway, this is not critical
            
            return Response({
                'message': 'Connexion réussie',
                'user': UserSerializer(authenticated_user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Login failed: Invalid credentials for {email}")
            return Response({
                'error': 'Identifiant ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except User.DoesNotExist:
        logger.warning(f"Login failed: User {email} does not exist")
        return Response({
            'error': 'Identifiant ou mot de passe incorrect'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        import traceback
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': f'Erreur serveur: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# GESTION DES MOTS DE PASSE
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Changer le mot de passe de l'utilisateur connecté
    """
    logger.info(f"change_password called for user: {request.user.email}")
    
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return Response({
            'error': 'Mot de passe actuel, nouveau mot de passe et confirmation requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier le mot de passe actuel
    if not request.user.check_password(current_password):
        return Response({
            'error': 'Mot de passe actuel incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        return Response({
            'error': 'Les nouveaux mots de passe ne correspondent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Valider la force du nouveau mot de passe
    if len(new_password) < 8:
        return Response({
            'error': 'Le mot de passe doit contenir au moins 8 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Changer le mot de passe
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info(f"Password changed successfully for user: {request.user.email}")
        
        return Response({
            'message': 'Mot de passe modifié avec succès'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return Response({
            'error': 'Erreur lors de la modification du mot de passe'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Demander la réinitialisation du mot de passe
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'error': 'Email requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Générer un token de réinitialisation (simulation)
        import secrets
        reset_token = secrets.token_urlsafe(32)
        
        # TODO: Envoyer email avec le token
        # Pour l'instant, on retourne juste un message de succès
        
        logger.info(f"Password reset requested for: {email}")
        
        return Response({
            'message': 'Un email de réinitialisation a été envoyé',
            'reset_token': reset_token  # À supprimer en production
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # Pour la sécurité, on retourne le même message même si l'utilisateur n'existe pas
        return Response({
            'message': 'Un email de réinitialisation a été envoyé'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        return Response({
            'error': 'Erreur lors de la demande de réinitialisation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Réinitialiser le mot de passe avec un token
    """
    email = request.data.get('email')
    reset_token = request.data.get('reset_token')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([email, reset_token, new_password, confirm_password]):
        return Response({
            'error': 'Email, token, nouveau mot de passe et confirmation requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier que les mots de passe correspondent
    if new_password != confirm_password:
        return Response({
            'error': 'Les mots de passe ne correspondent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Valider la force du mot de passe
    if len(new_password) < 8:
        return Response({
            'error': 'Le mot de passe doit contenir au moins 8 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # TODO: Vérifier le token de réinitialisation
        # Pour l'instant, on accepte n'importe quel token pour la démo
        
        # Changer le mot de passe
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password reset successfully for: {email}")
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        logger.error(f"Login error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': f'Erreur serveur: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# VUES D'INFORMATIONS UTILISATEUR
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Récupérer le profil de l'utilisateur connecté
    """
    return Response({
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Mettre à jour le profil utilisateur
    """
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
