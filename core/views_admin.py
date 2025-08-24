# -*- coding: utf-8 -*-
"""
Vues Web Admin pour la plateforme XAMILA
Gestion complète du back-office administrateur
"""

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination

from .models import User, SGI, Contract, QuizQuestion, OTP, RefreshToken
from .serializers import UserSerializer
from .permissions import IsAdminUser

User = get_user_model()


class AdminPagination(PageNumberPagination):
    """Pagination personnalisée pour l'admin"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== GESTION COMPLÈTE DES UTILISATEURS =====

class AdminUserListView(ListAPIView):
    """
    Liste complète des utilisateurs avec filtres avancés
    GET /api/admin/users/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminPagination
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Filtres par paramètres de requête
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(
                Q(country_of_residence__icontains=country) |
                Q(country_of_origin__icontains=country)
            )
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Ajouter des statistiques globales
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Statistiques par rôle
        role_stats = {}
        for role_code, role_name in User.ROLE_CHOICES:
            role_stats[role_code] = User.objects.filter(role=role_code).count()
        
        # Utilisateurs récents (7 derniers jours)
        week_ago = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(created_at__gte=week_ago).count()
        
        response.data['statistics'] = {
            'total_users': total_users,
            'verified_users': verified_users,
            'active_users': active_users,
            'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
            'role_distribution': role_stats,
            'recent_registrations': recent_users
        }
        
        return response


class AdminUserDetailView(RetrieveAPIView):
    """
    Détails complets d'un utilisateur
    GET /api/admin/users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        # Informations supplémentaires pour l'admin
        additional_data = {
            'connection_logs': {
                'last_login': user.last_login,
                'total_logins': RefreshToken.objects.filter(user=user).count(),
                'active_sessions': RefreshToken.objects.filter(
                    user=user,
                    expires_at__gt=timezone.now()
                ).count()
            },
            'otp_history': {
                'total_otp_sent': OTP.objects.filter(user=user).count(),
                'last_otp': OTP.objects.filter(user=user).order_by('-created_at').first(),
                'failed_attempts': OTP.objects.filter(user=user, is_used=False).count()
            },
            'account_activity': {
                'created_at': user.created_at,
                'updated_at': user.updated_at,
                'days_since_registration': (timezone.now() - user.created_at).days,
                'profile_completion': self._calculate_profile_completion(user)
            }
        }
        
        # Si c'est un manager SGI, ajouter les infos SGI
        if user.role == 'SGI_MANAGER':
            try:
                sgi = SGI.objects.get(manager=user)
                additional_data['sgi_info'] = {
                    'sgi_id': sgi.id,
                    'sgi_name': sgi.name,
                    'sgi_status': 'active' if sgi.is_active else 'inactive',
                    'contracts_count': Contract.objects.filter(sgi=sgi).count()
                }
            except SGI.DoesNotExist:
                additional_data['sgi_info'] = None
        
        response_data = serializer.data
        response_data['admin_details'] = additional_data
        
        return Response(response_data)
    
    def _calculate_profile_completion(self, user):
        """Calcule le pourcentage de complétion du profil"""
        fields = ['first_name', 'last_name', 'phone', 'country_of_residence', 'country_of_origin']
        completed = sum(1 for field in fields if getattr(user, field))
        return round((completed / len(fields)) * 100, 2)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_user_action(request, user_id):
    """
    Actions administratives sur un utilisateur
    POST /api/admin/users/{id}/action/
    
    Actions possibles:
    - activate: Activer le compte
    - deactivate: Désactiver le compte
    - verify: Marquer comme vérifié
    - unverify: Retirer la vérification
    - reset_password: Réinitialiser le mot de passe
    - send_otp: Envoyer un nouveau code OTP
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')
    reason = request.data.get('reason', '')
    
    if action == 'activate':
        user.is_active = True
        user.save()
        message = f'Compte activé. Raison: {reason}' if reason else 'Compte activé'
        
    elif action == 'deactivate':
        user.is_active = False
        user.save()
        message = f'Compte désactivé. Raison: {reason}' if reason else 'Compte désactivé'
        
    elif action == 'verify':
        user.is_verified = True
        user.email_verified = True
        user.save()
        message = 'Utilisateur marqué comme vérifié'
        
    elif action == 'unverify':
        user.is_verified = False
        user.email_verified = False
        user.save()
        message = 'Vérification retirée'
        
    elif action == 'reset_password':
        # Générer un nouveau mot de passe temporaire
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.set_password(temp_password)
        user.save()
        
        # TODO: Envoyer le nouveau mot de passe par email
        message = f'Mot de passe réinitialisé. Nouveau mot de passe: {temp_password}'
        
    elif action == 'send_otp':
        from .utils import generate_otp_code, send_otp_email
        
        # Générer et envoyer un nouveau code OTP
        otp_code = generate_otp_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            code=otp_code,
            otp_type='ADMIN_VERIFICATION',
            expires_at=expires_at
        )
        
        email_sent = send_otp_email(user, otp_code, 'ADMIN_VERIFICATION')
        message = 'Nouveau code OTP envoyé' if email_sent else 'Erreur lors de l\'envoi du code OTP'
        
    else:
        return Response({
            'error': 'Action non reconnue. Actions disponibles: activate, deactivate, verify, unverify, reset_password, send_otp'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Log de l'action admin (à implémenter plus tard)
    # AdminLog.objects.create(
    #     admin_user=request.user,
    #     target_user=user,
    #     action=action,
    #     reason=reason
    # )
    
    return Response({
        'message': message,
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Statistiques pour le tableau de bord admin
    GET /api/admin/dashboard/stats/
    """
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Statistiques utilisateurs
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    new_users_today = User.objects.filter(created_at__date=today).count()
    new_users_week = User.objects.filter(created_at__gte=week_ago).count()
    new_users_month = User.objects.filter(created_at__gte=month_ago).count()
    
    # Statistiques par rôle
    role_stats = {}
    for role_code, role_name in User.ROLE_CHOICES:
        role_stats[role_code] = {
            'name': role_name,
            'count': User.objects.filter(role=role_code).count(),
            'active': User.objects.filter(role=role_code, is_active=True).count()
        }
    
    # Statistiques SGI
    total_sgis = SGI.objects.count()
    active_sgis = SGI.objects.filter(is_active=True).count()
    pending_sgis = SGI.objects.filter(is_active=False).count()
    
    # Statistiques contrats
    total_contracts = Contract.objects.count()
    pending_contracts = Contract.objects.filter(status='PENDING').count()
    approved_contracts = Contract.objects.filter(status='APPROVED').count()
    
    # Statistiques OTP
    otp_sent_today = OTP.objects.filter(created_at__date=today).count()
    otp_success_rate = 0
    if otp_sent_today > 0:
        otp_used_today = OTP.objects.filter(created_at__date=today, is_used=True).count()
        otp_success_rate = round((otp_used_today / otp_sent_today) * 100, 2)
    
    # Évolution des inscriptions (30 derniers jours)
    registration_evolution = []
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        count = User.objects.filter(created_at__date=date).count()
        registration_evolution.append({
            'date': date.isoformat(),
            'count': count
        })
    registration_evolution.reverse()
    
    return Response({
        'users': {
            'total': total_users,
            'active': active_users,
            'verified': verified_users,
            'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
            'new_today': new_users_today,
            'new_week': new_users_week,
            'new_month': new_users_month,
            'by_role': role_stats
        },
        'sgis': {
            'total': total_sgis,
            'active': active_sgis,
            'pending': pending_sgis,
            'approval_rate': round((active_sgis / total_sgis * 100), 2) if total_sgis > 0 else 0
        },
        'contracts': {
            'total': total_contracts,
            'pending': pending_contracts,
            'approved': approved_contracts,
            'approval_rate': round((approved_contracts / total_contracts * 100), 2) if total_contracts > 0 else 0
        },
        'otp': {
            'sent_today': otp_sent_today,
            'success_rate': otp_success_rate
        },
        'registration_evolution': registration_evolution,
        'last_updated': now.isoformat()
    })


# ===== GESTION DES SGI =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_sgi_list(request):
    """
    Liste des SGI avec informations détaillées pour l'admin
    GET /api/admin/sgis/
    """
    sgis = SGI.objects.all().order_by('-created_at')
    
    # Filtres
    status_filter = request.query_params.get('status', None)
    if status_filter == 'active':
        sgis = sgis.filter(is_active=True)
    elif status_filter == 'pending':
        sgis = sgis.filter(is_active=False)
    
    search = request.query_params.get('search', None)
    if search:
        sgis = sgis.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(manager__email__icontains=search)
        )
    
    sgi_data = []
    for sgi in sgis:
        contracts_count = Contract.objects.filter(sgi=sgi).count()
        pending_contracts = Contract.objects.filter(sgi=sgi, status='PENDING').count()
        
        sgi_data.append({
            'id': sgi.id,
            'name': sgi.name,
            'description': sgi.description,
            'manager': {
                'id': sgi.manager.id,
                'name': f"{sgi.manager.first_name} {sgi.manager.last_name}",
                'email': sgi.manager.email,
                'phone': sgi.manager.phone
            },
            'is_active': sgi.is_active,
            'created_at': sgi.created_at,
            'updated_at': sgi.updated_at,
            'address': sgi.address,
            'website': sgi.website,
            'contracts': {
                'total': contracts_count,
                'pending': pending_contracts,
                'approved': contracts_count - pending_contracts
            }
        })
    
    return Response({
        'sgis': sgi_data,
        'total_count': len(sgi_data)
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_sgi_action(request, sgi_id):
    """
    Actions administratives sur une SGI
    POST /api/admin/sgis/{id}/action/
    
    Actions: approve, reject, suspend, reactivate
    """
    try:
        sgi = SGI.objects.get(id=sgi_id)
    except SGI.DoesNotExist:
        return Response({
            'error': 'SGI non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')
    reason = request.data.get('reason', '')
    
    if action == 'approve':
        sgi.is_active = True
        sgi.save()
        message = 'SGI approuvée et activée'
        
        # TODO: Envoyer email de confirmation au manager
        
    elif action == 'reject':
        sgi.is_active = False
        sgi.save()
        message = f'SGI rejetée. Raison: {reason}' if reason else 'SGI rejetée'
        
        # TODO: Envoyer email de rejet au manager
        
    elif action == 'suspend':
        sgi.is_active = False
        sgi.save()
        message = f'SGI suspendue. Raison: {reason}' if reason else 'SGI suspendue'
        
    elif action == 'reactivate':
        sgi.is_active = True
        sgi.save()
        message = 'SGI réactivée'
        
    else:
        return Response({
            'error': 'Action non reconnue. Actions disponibles: approve, reject, suspend, reactivate'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': message,
        'sgi': {
            'id': sgi.id,
            'name': sgi.name,
            'is_active': sgi.is_active,
            'updated_at': sgi.updated_at
        }
    })


# ===== GESTION DU CONTENU E-LEARNING =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_content_stats(request):
    """
    Statistiques du contenu e-learning
    GET /api/admin/content/stats/
    """
    total_questions = QuizQuestion.objects.count()
    questions_by_category = QuizQuestion.objects.values('category').annotate(count=Count('id'))
    questions_by_difficulty = QuizQuestion.objects.values('difficulty').annotate(count=Count('id'))
    questions_by_type = QuizQuestion.objects.values('question_type').annotate(count=Count('id'))
    
    # Questions créées récemment
    week_ago = timezone.now() - timedelta(days=7)
    recent_questions = QuizQuestion.objects.filter(created_at__gte=week_ago).count()
    
    return Response({
        'questions': {
            'total': total_questions,
            'recent': recent_questions,
            'by_category': list(questions_by_category),
            'by_difficulty': list(questions_by_difficulty),
            'by_type': list(questions_by_type)
        },
        'last_updated': timezone.now().isoformat()
    })


# ===== LOGS ET AUDIT =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_activity_logs(request):
    """
    Logs d'activité pour audit
    GET /api/admin/logs/
    """
    # Pour l'instant, on retourne les dernières connexions et créations OTP
    recent_logins = RefreshToken.objects.select_related('user').order_by('-created_at')[:50]
    recent_otps = OTP.objects.select_related('user').order_by('-created_at')[:50]
    
    login_data = []
    for token in recent_logins:
        login_data.append({
            'user': {
                'id': token.user.id,
                'username': token.user.username,
                'email': token.user.email,
                'role': token.user.role
            },
            'action': 'LOGIN',
            'timestamp': token.created_at,
            'expires_at': token.expires_at
        })
    
    otp_data = []
    for otp in recent_otps:
        otp_data.append({
            'user': {
                'id': otp.user.id,
                'username': otp.user.username,
                'email': otp.user.email,
                'role': otp.user.role
            },
            'action': f'OTP_{otp.otp_type}',
            'timestamp': otp.created_at,
            'is_used': otp.is_used,
            'expires_at': otp.expires_at
        })
    
    # Combiner et trier par date
    all_activities = login_data + otp_data
    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response({
        'activities': all_activities[:100],  # Limiter à 100 entrées
        'total_count': len(all_activities)
    })
