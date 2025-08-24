# -*- coding: utf-8 -*-
"""
Vues avancées Web Admin pour la plateforme XAMILA
Gestion avancée des SGI, contrats, et fonctionnalités business
"""

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta, datetime
import csv
import json
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView

from .models import User, SGI, Contract, QuizQuestion, OTP, RefreshToken
from .serializers_admin import (
    AdminSGISerializer, AdminContractSerializer, AdminQuizQuestionSerializer,
    AdminReportFilterSerializer, AdminBulkActionSerializer
)
from .permissions import IsAdminUser

User = get_user_model()


# ===== GESTION AVANCÉE DES SGI =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_sgi_analytics(request):
    """
    Analytics avancées des SGI
    GET /api/admin/sgis/analytics/
    """
    # Statistiques globales SGI
    total_sgis = SGI.objects.count()
    active_sgis = SGI.objects.filter(is_active=True).count()
    pending_sgis = SGI.objects.filter(is_active=False).count()
    
    # Performance des SGI
    sgi_performance = []
    for sgi in SGI.objects.filter(is_active=True):
        contracts = Contract.objects.filter(sgi=sgi)
        total_contracts = contracts.count()
        approved_contracts = contracts.filter(status='APPROVED').count()
        
        performance_data = {
            'sgi_id': sgi.id,
            'sgi_name': sgi.name,
            'manager': f"{sgi.manager.first_name} {sgi.manager.last_name}",
            'total_contracts': total_contracts,
            'approved_contracts': approved_contracts,
            'approval_rate': round((approved_contracts / total_contracts * 100), 2) if total_contracts > 0 else 0,
            'total_investment': contracts.filter(status='APPROVED').aggregate(
                total=Sum('investment_amount')
            )['total'] or 0,
            'average_investment': contracts.filter(status='APPROVED').aggregate(
                avg=Avg('investment_amount')
            )['avg'] or 0,
            'created_at': sgi.created_at
        }
        sgi_performance.append(performance_data)
    
    # Trier par taux d'approbation
    sgi_performance.sort(key=lambda x: x['approval_rate'], reverse=True)
    
    # Top 5 SGI par performance
    top_sgis = sgi_performance[:5]
    
    # Évolution des inscriptions SGI (30 derniers jours)
    now = timezone.now()
    sgi_evolution = []
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        count = SGI.objects.filter(created_at__date=date).count()
        sgi_evolution.append({
            'date': date.isoformat(),
            'count': count
        })
    sgi_evolution.reverse()
    
    return Response({
        'overview': {
            'total_sgis': total_sgis,
            'active_sgis': active_sgis,
            'pending_sgis': pending_sgis,
            'activation_rate': round((active_sgis / total_sgis * 100), 2) if total_sgis > 0 else 0
        },
        'performance_ranking': sgi_performance,
        'top_performers': top_sgis,
        'registration_evolution': sgi_evolution,
        'last_updated': now.isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_sgi_bulk_action(request):
    """
    Actions en lot sur les SGI
    POST /api/admin/sgis/bulk-action/
    """
    serializer = AdminBulkActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    sgi_ids = serializer.validated_data['ids']
    action = serializer.validated_data['action']
    reason = serializer.validated_data.get('reason', '')
    
    sgis = SGI.objects.filter(id__in=sgi_ids)
    updated_count = 0
    
    if action == 'approve':
        updated_count = sgis.update(is_active=True)
        message = f'{updated_count} SGI(s) approuvée(s)'
        
    elif action == 'reject':
        updated_count = sgis.update(is_active=False)
        message = f'{updated_count} SGI(s) rejetée(s)'
        
    elif action == 'suspend':
        updated_count = sgis.update(is_active=False)
        message = f'{updated_count} SGI(s) suspendue(s)'
        
    else:
        return Response({
            'error': 'Action non reconnue'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': message,
        'updated_count': updated_count,
        'reason': reason
    })


# ===== GESTION AVANCÉE DES CONTRATS =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_contracts_dashboard(request):
    """
    Tableau de bord des contrats
    GET /api/admin/contracts/dashboard/
    """
    # Statistiques globales
    total_contracts = Contract.objects.count()
    pending_contracts = Contract.objects.filter(status='PENDING').count()
    approved_contracts = Contract.objects.filter(status='APPROVED').count()
    rejected_contracts = Contract.objects.filter(status='REJECTED').count()
    
    # Montants d'investissement
    total_investment = Contract.objects.filter(status='APPROVED').aggregate(
        total=Sum('investment_amount')
    )['total'] or 0
    
    average_investment = Contract.objects.filter(status='APPROVED').aggregate(
        avg=Avg('investment_amount')
    )['avg'] or 0
    
    # Contrats par SGI
    contracts_by_sgi = Contract.objects.values(
        'sgi__name', 'sgi__id'
    ).annotate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='APPROVED')),
        pending=Count('id', filter=Q(status='PENDING')),
        total_amount=Sum('investment_amount', filter=Q(status='APPROVED'))
    ).order_by('-total')[:10]
    
    # Évolution des contrats (30 derniers jours)
    now = timezone.now()
    contracts_evolution = []
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        daily_stats = {
            'date': date.isoformat(),
            'created': Contract.objects.filter(created_at__date=date).count(),
            'approved': Contract.objects.filter(
                updated_at__date=date, status='APPROVED'
            ).count(),
            'rejected': Contract.objects.filter(
                updated_at__date=date, status='REJECTED'
            ).count()
        }
        contracts_evolution.append(daily_stats)
    contracts_evolution.reverse()
    
    # Temps de traitement moyen
    processed_contracts = Contract.objects.exclude(status='PENDING')
    avg_processing_time = 0
    if processed_contracts.exists():
        processing_times = []
        for contract in processed_contracts:
            if contract.updated_at:
                delta = contract.updated_at - contract.created_at
                processing_times.append(delta.days)
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
    
    return Response({
        'overview': {
            'total_contracts': total_contracts,
            'pending_contracts': pending_contracts,
            'approved_contracts': approved_contracts,
            'rejected_contracts': rejected_contracts,
            'approval_rate': round((approved_contracts / total_contracts * 100), 2) if total_contracts > 0 else 0,
            'total_investment': float(total_investment),
            'average_investment': float(average_investment),
            'avg_processing_time_days': round(avg_processing_time, 1)
        },
        'contracts_by_sgi': list(contracts_by_sgi),
        'evolution': contracts_evolution,
        'last_updated': now.isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_contracts_list(request):
    """
    Liste détaillée des contrats avec filtres
    GET /api/admin/contracts/
    """
    contracts = Contract.objects.select_related('client', 'sgi', 'sgi__manager').order_by('-created_at')
    
    # Filtres
    status_filter = request.query_params.get('status', None)
    if status_filter:
        contracts = contracts.filter(status=status_filter.upper())
    
    sgi_id = request.query_params.get('sgi_id', None)
    if sgi_id:
        contracts = contracts.filter(sgi_id=sgi_id)
    
    min_amount = request.query_params.get('min_amount', None)
    if min_amount:
        contracts = contracts.filter(investment_amount__gte=float(min_amount))
    
    max_amount = request.query_params.get('max_amount', None)
    if max_amount:
        contracts = contracts.filter(investment_amount__lte=float(max_amount))
    
    search = request.query_params.get('search', None)
    if search:
        contracts = contracts.filter(
            Q(client__email__icontains=search) |
            Q(client__first_name__icontains=search) |
            Q(client__last_name__icontains=search) |
            Q(sgi__name__icontains=search)
        )
    
    # Pagination
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = contracts.count()
    contracts_page = contracts[start:end]
    
    # Sérialiser les données
    contracts_data = []
    for contract in contracts_page:
        contracts_data.append({
            'id': contract.id,
            'client': {
                'id': contract.client.id,
                'name': f"{contract.client.first_name} {contract.client.last_name}",
                'email': contract.client.email,
                'phone': contract.client.phone
            },
            'sgi': {
                'id': contract.sgi.id,
                'name': contract.sgi.name,
                'manager': f"{contract.sgi.manager.first_name} {contract.sgi.manager.last_name}"
            },
            'investment_amount': float(contract.investment_amount),
            'duration_months': contract.duration_months,
            'status': contract.status,
            'created_at': contract.created_at,
            'updated_at': contract.updated_at,
            'processing_time_days': (contract.updated_at - contract.created_at).days if contract.updated_at else None
        })
    
    return Response({
        'contracts': contracts_data,
        'pagination': {
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_contract_action(request, contract_id):
    """
    Actions administratives sur un contrat
    POST /api/admin/contracts/{id}/action/
    """
    try:
        contract = Contract.objects.get(id=contract_id)
    except Contract.DoesNotExist:
        return Response({
            'error': 'Contrat non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')
    reason = request.data.get('reason', '')
    
    if action == 'approve':
        contract.status = 'APPROVED'
        contract.save()
        message = 'Contrat approuvé'
        
        # TODO: Envoyer notification au client et à la SGI
        
    elif action == 'reject':
        contract.status = 'REJECTED'
        contract.save()
        message = f'Contrat rejeté. Raison: {reason}' if reason else 'Contrat rejeté'
        
        # TODO: Envoyer notification de rejet
        
    elif action == 'request_info':
        # Demander des informations supplémentaires
        message = f'Informations supplémentaires demandées: {reason}'
        
        # TODO: Envoyer email avec demande d'informations
        
    else:
        return Response({
            'error': 'Action non reconnue. Actions disponibles: approve, reject, request_info'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': message,
        'contract': {
            'id': contract.id,
            'status': contract.status,
            'updated_at': contract.updated_at
        }
    })


# ===== REPORTING ET EXPORT =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_export_users(request):
    """
    Export des utilisateurs en CSV
    GET /api/admin/export/users/
    """
    # Filtres
    role = request.query_params.get('role', None)
    is_verified = request.query_params.get('is_verified', None)
    country = request.query_params.get('country', None)
    
    users = User.objects.all()
    
    if role:
        users = users.filter(role=role)
    if is_verified is not None:
        users = users.filter(is_verified=is_verified.lower() == 'true')
    if country:
        users = users.filter(
            Q(country_of_residence__icontains=country) |
            Q(country_of_origin__icontains=country)
        )
    
    # Créer le fichier CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Username', 'Email', 'Prénom', 'Nom', 'Téléphone', 'Rôle',
        'Actif', 'Vérifié', 'Pays de résidence', 'Pays d\'origine',
        'Date d\'inscription', 'Dernière connexion'
    ])
    
    for user in users:
        writer.writerow([
            str(user.id),
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.phone,
            user.get_role_display(),
            'Oui' if user.is_active else 'Non',
            'Oui' if user.is_verified else 'Non',
            user.country_of_residence,
            user.country_of_origin,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Jamais'
        ])
    
    return response


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_business_intelligence(request):
    """
    Business Intelligence et métriques avancées
    GET /api/admin/bi/
    """
    now = timezone.now()
    
    # Métriques de croissance
    current_month = now.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    current_month_users = User.objects.filter(created_at__gte=current_month).count()
    last_month_users = User.objects.filter(
        created_at__gte=last_month,
        created_at__lt=current_month
    ).count()
    
    user_growth_rate = 0
    if last_month_users > 0:
        user_growth_rate = round(((current_month_users - last_month_users) / last_month_users) * 100, 2)
    
    # Métriques d'engagement
    active_users_7d = User.objects.filter(last_login__gte=now - timedelta(days=7)).count()
    active_users_30d = User.objects.filter(last_login__gte=now - timedelta(days=30)).count()
    total_users = User.objects.count()
    
    engagement_7d = round((active_users_7d / total_users * 100), 2) if total_users > 0 else 0
    engagement_30d = round((active_users_30d / total_users * 100), 2) if total_users > 0 else 0
    
    # Métriques financières
    total_investment = Contract.objects.filter(status='APPROVED').aggregate(
        total=Sum('investment_amount')
    )['total'] or 0
    
    monthly_investment = Contract.objects.filter(
        status='APPROVED',
        updated_at__gte=current_month
    ).aggregate(total=Sum('investment_amount'))['total'] or 0
    
    # Conversion funnel
    total_registrations = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    users_with_contracts = Contract.objects.values('client').distinct().count()
    approved_contracts = Contract.objects.filter(status='APPROVED').count()
    
    conversion_rates = {
        'registration_to_verification': round((verified_users / total_registrations * 100), 2) if total_registrations > 0 else 0,
        'verification_to_contract': round((users_with_contracts / verified_users * 100), 2) if verified_users > 0 else 0,
        'contract_to_approval': round((approved_contracts / Contract.objects.count() * 100), 2) if Contract.objects.count() > 0 else 0
    }
    
    # Top pays par utilisateurs
    country_stats = User.objects.values('country_of_residence').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'growth_metrics': {
            'user_growth_rate_monthly': user_growth_rate,
            'new_users_current_month': current_month_users,
            'new_users_last_month': last_month_users
        },
        'engagement_metrics': {
            'active_users_7d': active_users_7d,
            'active_users_30d': active_users_30d,
            'engagement_rate_7d': engagement_7d,
            'engagement_rate_30d': engagement_30d
        },
        'financial_metrics': {
            'total_investment': float(total_investment),
            'monthly_investment': float(monthly_investment),
            'average_contract_value': float(total_investment / approved_contracts) if approved_contracts > 0 else 0
        },
        'conversion_funnel': conversion_rates,
        'geographic_distribution': list(country_stats),
        'generated_at': now.isoformat()
    })


# ===== SYSTÈME DE MATCHING SGI =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_matching_analytics(request):
    """
    Analytics du système de matching SGI
    GET /api/admin/matching/analytics/
    """
    # Statistiques de matching (à implémenter avec le système de matching)
    return Response({
        'matching_stats': {
            'total_matches': 0,
            'successful_matches': 0,
            'conversion_rate': 0,
            'average_match_score': 0
        },
        'algorithm_performance': {
            'accuracy': 0,
            'precision': 0,
            'recall': 0
        },
        'top_matching_criteria': [],
        'sgi_match_distribution': [],
        'note': 'Système de matching à implémenter'
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_configure_matching(request):
    """
    Configuration du système de matching
    POST /api/admin/matching/configure/
    """
    # Configuration des règles de matching (à implémenter)
    return Response({
        'message': 'Configuration du matching mise à jour',
        'note': 'Système de matching à implémenter'
    })
