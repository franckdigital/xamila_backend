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

from .models import User, SGI, Contract, QuizQuestion, OTP, RefreshToken, SavingsChallenge, ChallengeParticipation, SavingsDeposit
from .models_sgi_manager import SGIManagerProfile
from .models_sgi import SGIManager, SGIManagerAssignment
from .serializers import UserSerializer
from .models_sgi import SGIAccountTerms
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
        
        # Si on reçoit un sgi_id et que le user est SGI_MANAGER, lier la SGI
        sgi_id = request.data.get('sgi_id')
        if sgi_id and (request.data.get('role') == 'SGI_MANAGER' or user.role == 'SGI_MANAGER'):
            try:
                sgi = SGI.objects.get(id=sgi_id)
                SGIManagerProfile.objects.update_or_create(user=user, defaults={'sgi': sgi})
            except SGI.DoesNotExist:
                pass
            try:
                manager_obj, _ = SGIManager.objects.get_or_create(user=user, defaults={
                    'professional_title': 'Manager SGI',
                    'license_number': f"LIC-{user.id}",
                    'years_of_experience': 0,
                    'professional_email': user.email or '',
                    'professional_phone': user.phone or '',
                })
                SGIManagerAssignment.objects.update_or_create(
                    sgi=sgi, manager=manager_obj,
                    defaults={'role': 'PRIMARY', 'permissions': ['ADMIN'], 'is_active': True}
                )
            except Exception:
                pass
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


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_sgi(request):
    """
    Créer une nouvelle SGI (basique) depuis l'admin
    POST /api/admin/sgis/create/
    Accepte: name (obligatoire), description, email, phone, address, website, is_active
    """
    data = request.data
    name = data.get('name')
    if not name:
        return Response({'error': 'Le nom de la SGI est obligatoire'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from decimal import Decimal
        # Champs requis supplémentaires dans le modèle SGI
        manager_name = data.get('manager_name') or 'Manager'
        manager_email = data.get('manager_email') or (data.get('email') or 'contact@xamila.finance')
        manager_phone = data.get('manager_phone') or ''
        min_investment_amount = data.get('min_investment_amount')
        try:
            min_investment_amount = Decimal(str(min_investment_amount)) if min_investment_amount is not None else Decimal('1000.00')
        except Exception:
            min_investment_amount = Decimal('1000.00')
        # Optionnels
        max_investment_amount = data.get('max_investment_amount')
        try:
            max_investment_amount = Decimal(str(max_investment_amount)) if max_investment_amount not in (None, '') else None
        except Exception:
            max_investment_amount = None
        def parse_decimal(val, default):
            try:
                return Decimal(str(val)) if val not in (None, '') else default
            except Exception:
                return default
        historical_performance = parse_decimal(data.get('historical_performance'), Decimal('0.00'))
        management_fees = parse_decimal(data.get('management_fees'), Decimal('2.00'))
        entry_fees = parse_decimal(data.get('entry_fees'), Decimal('0.00'))
        is_verified = bool(data.get('is_verified', False))

        # Créer la SGI de base
        logo_file = request.FILES.get('logo')
        sgi = SGI.objects.create(
            name=name,
            description=data.get('description', ''),
            email=(data.get('email') or 'contact@xamila.finance'),
            phone=data.get('phone', ''),
            address=data.get('address', 'Adresse à renseigner'),
            website=data.get('website', ''),
            logo=logo_file if logo_file else None,
            manager_name=manager_name,
            manager_email=manager_email,
            manager_phone=manager_phone,
            min_investment_amount=min_investment_amount,
            max_investment_amount=max_investment_amount,
            historical_performance=historical_performance,
            management_fees=management_fees,
            entry_fees=entry_fees,
            is_active=bool(data.get('is_active', True))
        )
        # Marquer vérifiée si demandé
        if is_verified and not sgi.is_verified:
            sgi.is_verified = True
            sgi.save(update_fields=['is_verified'])

        # Créer/peupler les Terms si des champs pertinents sont fournis
        import json
        def parse_bool(val, default=False):
            if isinstance(val, bool):
                return val
            if val is None:
                return default
            s = str(val).lower()
            return s in ('1', 'true', 'yes', 'on')
        def parse_json_list(val):
            if val is None or val == "":
                return []
            if isinstance(val, (list, tuple)):
                return list(val)
            try:
                return json.loads(val)
            except Exception:
                # fallback split comma
                return [x.strip() for x in str(val).split(',') if x.strip()]
        def parse_decimal_nullable(val):
            try:
                from decimal import Decimal as D
                return D(str(val)) if val not in (None, '') else None
            except Exception:
                return None

        terms_payload_present = any(k in request.data for k in [
            'country','headquarters_address','director_name','profile','is_digital_opening',
            'has_minimum_amount','minimum_amount_value','has_opening_fees','opening_fees_amount',
            'deposit_methods','is_bank_subsidiary','parent_bank_name','custody_fees',
            'account_maintenance_fees','brokerage_fees_transactions_ordinary','brokerage_fees_files',
            'brokerage_fees_transactions','transfer_account_fees','transfer_securities_fees','pledge_fees',
            'redemption_methods','preferred_customer_banks'
        ])

        if terms_payload_present:
            SGIAccountTerms.objects.update_or_create(
                sgi=sgi,
                defaults={
                    'country': data.get('country', '') or '',
                    'headquarters_address': data.get('headquarters_address', '') or '',
                    'director_name': data.get('director_name', '') or '',
                    'profile': data.get('profile', '') or '',
                    'is_digital_opening': parse_bool(data.get('is_digital_opening'), True),
                    'has_minimum_amount': parse_bool(data.get('has_minimum_amount'), False),
                    'minimum_amount_value': parse_decimal_nullable(data.get('minimum_amount_value')),
                    'has_opening_fees': parse_bool(data.get('has_opening_fees'), False),
                    'opening_fees_amount': parse_decimal_nullable(data.get('opening_fees_amount')),
                    'deposit_methods': parse_json_list(data.get('deposit_methods')),
                    'is_bank_subsidiary': parse_bool(data.get('is_bank_subsidiary'), False),
                    'parent_bank_name': data.get('parent_bank_name') or None,
                    'custody_fees': parse_decimal_nullable(data.get('custody_fees')),
                    'account_maintenance_fees': parse_decimal_nullable(data.get('account_maintenance_fees')),
                    'brokerage_fees_transactions_ordinary': parse_decimal_nullable(data.get('brokerage_fees_transactions_ordinary')),
                    'brokerage_fees_files': parse_decimal_nullable(data.get('brokerage_fees_files')),
                    'brokerage_fees_transactions': parse_decimal_nullable(data.get('brokerage_fees_transactions')),
                    'transfer_account_fees': parse_decimal_nullable(data.get('transfer_account_fees')),
                    'transfer_securities_fees': parse_decimal_nullable(data.get('transfer_securities_fees')),
                    'pledge_fees': parse_decimal_nullable(data.get('pledge_fees')),
                    'redemption_methods': parse_json_list(data.get('redemption_methods')),
                    'preferred_customer_banks': parse_json_list(data.get('preferred_customer_banks')),
                }
            )

        return Response({
            'id': sgi.id,
            'name': sgi.name,
            'description': sgi.description,
            'email': sgi.email,
            'phone': sgi.phone,
            'address': sgi.address,
            'website': sgi.website,
            'logo': sgi.logo.url if sgi.logo else None,
            'manager_name': sgi.manager_name,
            'manager_email': sgi.manager_email,
            'manager_phone': sgi.manager_phone,
            'min_investment_amount': str(sgi.min_investment_amount),
            'max_investment_amount': str(sgi.max_investment_amount) if sgi.max_investment_amount is not None else None,
            'historical_performance': str(sgi.historical_performance),
            'management_fees': str(sgi.management_fees),
            'entry_fees': str(sgi.entry_fees),
            'is_active': sgi.is_active,
            'is_verified': sgi.is_verified,
            'created_at': sgi.created_at,
            'updated_at': sgi.updated_at,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Erreur lors de la création de la SGI: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


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


# ===== GESTION DES DÉFIS ÉPARGNE =====

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_challenges(request):
    """
    Gestion des défis épargne
    GET /api/admin/challenges/ - Liste des défis
    POST /api/admin/challenges/ - Créer un nouveau défi
    """
    if request.method == 'GET':
        challenges = SavingsChallenge.objects.all().order_by('-created_at')
        
        # Filtres
        status_filter = request.query_params.get('status', None)
        if status_filter:
            challenges = challenges.filter(status=status_filter)
        
        search = request.query_params.get('search', None)
        if search:
            challenges = challenges.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        challenge_data = []
        for challenge in challenges:
            participants_count = ChallengeParticipation.objects.filter(challenge=challenge).count()
            total_saved = SavingsDeposit.objects.filter(
                participation__challenge=challenge
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            challenge_data.append({
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'target_amount': float(challenge.target_amount),
                'minimum_deposit': float(challenge.minimum_deposit),
                'duration_days': challenge.duration_days,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'status': challenge.status,
                'participants_count': participants_count,
                'total_saved': float(total_saved),
                'created_at': challenge.created_at.isoformat(),
                'updated_at': challenge.updated_at.isoformat()
            })
        
        return Response(challenge_data)
    
    elif request.method == 'POST':
        data = request.data
        
        try:
            challenge = SavingsChallenge.objects.create(
                title=data['title'],
                description=data['description'],
                target_amount=data['target_amount'],
                minimum_deposit=data['minimum_deposit'],
                duration_days=data.get('duration_days', 180),
                start_date=data['start_date'],
                end_date=data['end_date'],
                status=data.get('status', 'ACTIVE')
            )
            
            participants_count = ChallengeParticipation.objects.filter(challenge=challenge).count()
            
            return Response({
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'target_amount': float(challenge.target_amount),
                'minimum_deposit': float(challenge.minimum_deposit),
                'duration_days': challenge.duration_days,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'status': challenge.status,
                'participants_count': participants_count,
                'created_at': challenge.created_at.isoformat(),
                'updated_at': challenge.updated_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la création du défi: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_challenge_detail(request, challenge_id):
    """
    Gestion d'un défi spécifique
    GET /api/admin/challenges/{id}/ - Détails du défi
    PUT /api/admin/challenges/{id}/ - Modifier le défi
    DELETE /api/admin/challenges/{id}/ - Supprimer le défi
    """
    try:
        challenge = SavingsChallenge.objects.get(id=challenge_id)
    except SavingsChallenge.DoesNotExist:
        return Response({
            'error': 'Défi non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        participants_count = ChallengeParticipation.objects.filter(challenge=challenge).count()
        total_saved = SavingsDeposit.objects.filter(
            participation__challenge=challenge
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Participants détaillés
        participants = ChallengeParticipation.objects.filter(
            challenge=challenge
        ).select_related('user')[:10]  # Limiter à 10 pour les performances
        
        participants_data = []
        for participation in participants:
            user_saved = SavingsDeposit.objects.filter(
                participation=participation
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            participants_data.append({
                'user_id': participation.user.id,
                'user_name': f"{participation.user.first_name} {participation.user.last_name}",
                'user_email': participation.user.email,
                'total_saved': float(user_saved),
                'progress_percentage': round((user_saved / challenge.target_amount) * 100, 2) if challenge.target_amount > 0 else 0,
                'joined_at': participation.created_at.isoformat()
            })
        
        return Response({
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'target_amount': float(challenge.target_amount),
            'minimum_deposit': float(challenge.minimum_deposit),
            'duration_days': challenge.duration_days,
            'start_date': challenge.start_date.isoformat(),
            'end_date': challenge.end_date.isoformat(),
            'status': challenge.status,
            'participants_count': participants_count,
            'total_saved': float(total_saved),
            'progress_percentage': round((total_saved / (challenge.target_amount * participants_count)) * 100, 2) if participants_count > 0 and challenge.target_amount > 0 else 0,
            'participants': participants_data,
            'created_at': challenge.created_at.isoformat(),
            'updated_at': challenge.updated_at.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.data
        
        try:
            challenge.title = data.get('title', challenge.title)
            challenge.description = data.get('description', challenge.description)
            challenge.target_amount = data.get('target_amount', challenge.target_amount)
            challenge.minimum_deposit = data.get('minimum_deposit', challenge.minimum_deposit)
            challenge.duration_days = data.get('duration_days', challenge.duration_days)
            challenge.start_date = data.get('start_date', challenge.start_date)
            challenge.end_date = data.get('end_date', challenge.end_date)
            challenge.status = data.get('status', challenge.status)
            challenge.save()
            
            participants_count = ChallengeParticipation.objects.filter(challenge=challenge).count()
            
            return Response({
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'target_amount': float(challenge.target_amount),
                'minimum_deposit': float(challenge.minimum_deposit),
                'duration_days': challenge.duration_days,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'status': challenge.status,
                'participants_count': participants_count,
                'updated_at': challenge.updated_at.isoformat()
            })
            
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la mise à jour: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Vérifier s'il y a des participants
        participants_count = ChallengeParticipation.objects.filter(challenge=challenge).count()
        if participants_count > 0:
            return Response({
                'error': f'Impossible de supprimer ce défi car il a {participants_count} participant(s). Désactivez-le plutôt.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        challenge.delete()
        return Response({
            'message': 'Défi supprimé avec succès'
        }, status=status.HTTP_204_NO_CONTENT)


# ===== GESTION DES UTILISATEURS - ENDPOINTS SUPPLÉMENTAIRES =====

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_user(request):
    """
    Créer un nouvel utilisateur depuis l'admin
    POST /api/admin/users/create/
    """
    data = request.data
    
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=data['username']).exists():
            return Response({
                'error': 'Ce nom d\'utilisateur existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=data['email']).exists():
            return Response({
                'error': 'Cet email est déjà utilisé'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            role=data.get('role', 'CUSTOMER'),
            age_range=data.get('age_range', ''),
            gender=data.get('gender', ''),
            country=data.get('country', ''),
            country_of_residence=data.get('country_of_residence', ''),
            country_of_origin=data.get('country_of_origin', ''),
            is_active=data.get('is_active', True),
            email_verified=data.get('email_verified', False)
        )
        
        # Lier à une SGI si fourni et rôle SGI_MANAGER
        sgi_id = data.get('sgi_id')
        if sgi_id and data.get('role') == 'SGI_MANAGER':
            try:
                sgi = SGI.objects.get(id=sgi_id)
                # 1) Essayer via SGIManagerProfile (lien direct user<->sgi)
                SGIManagerProfile.objects.update_or_create(user=user, defaults={'sgi': sgi})
            except SGI.DoesNotExist:
                pass
            try:
                # 2) Aussi maintenir l'autre modèle (SGIManager + Assignment) si utilisé
                manager_obj, _ = SGIManager.objects.get_or_create(user=user, defaults={
                    'professional_title': 'Manager SGI',
                    'license_number': f"LIC-{user.id}",
                    'years_of_experience': 0,
                    'professional_email': user.email or '',
                    'professional_phone': user.phone or '',
                })
                SGIManagerAssignment.objects.update_or_create(
                    sgi=sgi, manager=manager_obj,
                    defaults={'role': 'PRIMARY', 'permissions': ['ADMIN'], 'is_active': True}
                )
            except Exception:
                # Pas bloquant si ce modèle alternatif n'est pas en usage
                pass
        
        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la création: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_update_user(request, user_id):
    """
    Modifier un utilisateur depuis l'admin
    PUT /api/admin/users/{id}/update/
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    
    try:
        # Vérifier l'unicité du nom d'utilisateur et email
        if 'username' in data and data['username'] != user.username:
            if User.objects.filter(username=data['username']).exists():
                return Response({
                    'error': 'Ce nom d\'utilisateur existe déjà'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            if User.objects.filter(email=data['email']).exists():
                return Response({
                    'error': 'Cet email est déjà utilisé'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = data['email']
        
        # Mettre à jour les autres champs
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data:
            user.role = data['role']
        if 'age_range' in data:
            user.age_range = data['age_range']
        if 'gender' in data:
            user.gender = data['gender']
        if 'country' in data:
            user.country = data['country']
        if 'country_of_residence' in data:
            user.country_of_residence = data['country_of_residence']
        if 'country_of_origin' in data:
            user.country_of_origin = data['country_of_origin']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'email_verified' in data:
            user.email_verified = data['email_verified']
        
        # Changer le mot de passe si fourni
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        user.save()
        
        return Response({
            'message': 'Utilisateur mis à jour avec succès',
            'user': UserSerializer(user).data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_user(request, user_id):
    """
    Supprimer un utilisateur depuis l'admin
    DELETE /api/admin/users/{id}/delete/
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier si l'utilisateur peut être supprimé
    if user.role == 'ADMIN' and User.objects.filter(role='ADMIN').count() == 1:
        return Response({
            'error': 'Impossible de supprimer le dernier administrateur'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier s'il y a des données liées
    if user.role == 'SGI_MANAGER':
        sgi_count = SGI.objects.filter(manager=user).count()
        if sgi_count > 0:
            return Response({
                'error': f'Impossible de supprimer cet utilisateur car il gère {sgi_count} SGI(s)'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    username = user.username
    user.delete()
    
    return Response({
        'message': f'Utilisateur {username} supprimé avec succès'
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_user_payment(request, user_id):
    """
    Activer/Désactiver le statut de paiement d'un utilisateur
    POST /api/admin/users/{id}/toggle-payment/
    """
    try:
        user = User.objects.get(id=user_id)
        user.paye = not user.paye
        user.save()
        
        return Response({
            'success': True,
            'message': f'Statut de paiement {"activé" if user.paye else "désactivé"} pour {user.username}',
            'paye': user.paye
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour du statut de paiement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_certificate(request, user_id):
    """
    Activer/Désactiver le certificat de réussite pour un utilisateur
    POST /api/admin/users/{id}/toggle-certificate/
    """
    try:
        user = User.objects.get(id=user_id)
        user.certif_reussite = not user.certif_reussite
        user.save()
        
        return Response({
            'success': True,
            'message': f'Certificat de réussite {"activé" if user.certif_reussite else "désactivé"} pour {user.username}',
            'certif_reussite': user.certif_reussite
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour du certificat: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_user_status(request, user_id):
    """
    Activer/Désactiver un utilisateur
    POST /api/admin/users/{id}/toggle-status/
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('is_active', not user.is_active)
    user.is_active = new_status
    user.save()
    
    return Response({
        'message': f'Utilisateur {"activé" if new_status else "désactivé"} avec succès',
        'user': {
            'id': user.id,
            'username': user.username,
            'is_active': user.is_active
        }
    })


# ===== GESTION DES PERMISSIONS ET RÔLES =====

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_role_permissions(request):
    """
    Gestion des permissions par rôle
    GET /api/admin/role-permissions/ - Obtenir les permissions par rôle
    POST /api/admin/role-permissions/ - Modifier une permission
    """
    # Permissions par défaut pour chaque rôle
    default_permissions = {
        'CUSTOMER': [
            'dashboard.view',
            'savings.plans',
            'savings.challenges',
            'portfolio.view',
            'sgi.access',
            'training.bourse'
        ],
        'SGI_MANAGER': [
            'dashboard.view',
            'dashboard.sgi_manager',
            'sgi.view',
            'sgi.manage',
            'sgi.clients',
            'savings.plans',
            'portfolio.view'
        ],
        'INSTRUCTOR': [
            'dashboard.view',
            'dashboard.instructor',
            'training.bourse',
            'training.create',
            'training.manage'
        ],
        'SUPPORT': [
            'dashboard.view',
            'dashboard.support',
            'support.tickets',
            'support.respond',
            'users.view'
        ],
        'ADMIN': [
            'dashboard.view',
            'dashboard.admin',
            'users.view',
            'users.create',
            'users.edit',
            'users.delete',
            'sgi.view',
            'sgi.manage',
            'training.bourse',
            'training.create',
            'training.manage',
            'support.tickets',
            'support.respond',
            'savings.plans',
            'savings.challenges',
            'portfolio.view',
            'sgi.access',
            'sgi.clients'
        ]
    }
    
    if request.method == 'GET':
        # Retourner les permissions par rôle
        role_permissions = []
        for role_code, role_name in User.ROLE_CHOICES:
            role_permissions.append({
                'role': role_code,
                'role_name': role_name,
                'permissions': default_permissions.get(role_code, [])
            })
        
        return Response(role_permissions)
    
    elif request.method == 'POST':
        # Modifier une permission (pour l'instant, on simule juste la réponse)
        role = request.data.get('role')
        permission = request.data.get('permission')
        enabled = request.data.get('enabled', True)
        
        if role not in dict(User.ROLE_CHOICES):
            return Response({
                'error': 'Rôle invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implémenter la sauvegarde réelle des permissions en base
        # Pour l'instant, on retourne juste un succès
        
        return Response({
            'message': f'Permission {permission} {"accordée" if enabled else "révoquée"} pour le rôle {role}',
            'role': role,
            'permission': permission,
            'enabled': enabled
        })
