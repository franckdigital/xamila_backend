"""
Vues pour les endpoints du dashboard multi-rôles
Fournit les données spécifiques à chaque type d'utilisateur
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
from datetime import datetime, timedelta
from .models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_dashboard_metrics(request):
    """Dashboard pour les clients CUSTOMER avec données dynamiques de la BD"""
    
    # Pour test temporaire, utiliser l'utilisateur test
    try:
        user = User.objects.get(email="test@xamila.com")
        logger.info(f"Dashboard request for test user: {user.email}")
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Test user not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Récupérer les données réelles depuis la base de données
    from .models_savings_challenge import ChallengeParticipation, SavingsAccount, SavingsGoal
    from django.db.models import Sum, Count, Avg
    
    # Calculs des données d'épargne réelles
    participations = ChallengeParticipation.objects.filter(user=user)
    savings_accounts = SavingsAccount.objects.filter(user=user, status='ACTIVE')
    savings_goals = SavingsGoal.objects.filter(user=user, status='ACTIVE')
    
    # Total épargné dans tous les défis
    total_savings = participations.aggregate(
        total=Sum('total_saved')
    )['total'] or 0
    
    # Solde total des comptes d'épargne
    account_balance = savings_accounts.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    # Défis complétés
    challenges_completed = participations.filter(status='COMPLETED').count()
    
    # Série actuelle (plus longue série parmi tous les défis)
    from django.db import models
    current_streak = participations.aggregate(
        max_streak=models.Max('current_streak')
    )['max_streak'] or 0
    
    # Objectif mensuel (somme des objectifs actifs)
    monthly_goal = savings_goals.aggregate(
        total_target=Sum('target_amount')
    )['total_target'] or 0
    
    # Portfolio value (total épargné + soldes comptes)
    portfolio_value = total_savings + account_balance
    
    # Dernière participation active
    last_participation = participations.filter(status='ACTIVE').order_by('-last_deposit_at').first()
    last_deposit = last_participation.last_deposit_at.date() if last_participation and last_participation.last_deposit_at else None
    
    savings_data = {
        'user_id': str(user.id),
        'user_name': user.get_full_name() or user.email,
        'user_role': user.role,
        'total_savings': float(total_savings),
        'monthly_goal': float(monthly_goal),
        'challenges_completed': challenges_completed,
        'current_streak': current_streak,
        'portfolio_value': float(portfolio_value),
        'account_balance': float(account_balance),
        'active_goals': savings_goals.count(),
        'active_participations': participations.filter(status='ACTIVE').count(),
        'last_deposit': last_deposit.isoformat() if last_deposit else None,
        'total_deposits': participations.aggregate(total=Sum('deposits_count'))['total'] or 0
    }
    
    logger.info(f"Returning dynamic dashboard data for {user.email}")
    return Response(savings_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_challenges_list(request):
    """Liste des défis d'épargne avec données dynamiques de la BD"""
    
    # Pour test temporaire, utiliser l'utilisateur test
    try:
        user = User.objects.get(email="test@xamila.com")
        logger.info(f"Challenges request for test user: {user.email}")
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Test user not found'}, status=status.HTTP_404_NOT_FOUND)
    
    from .models_savings_challenge import SavingsChallenge, ChallengeParticipation
    
    # Récupérer les défis auxquels l'utilisateur participe
    user_participations = ChallengeParticipation.objects.filter(
        user=user
    ).select_related('challenge')
    
    challenges = []
    for participation in user_participations:
        challenge = participation.challenge
        
        # Compter le nombre total de participants
        participants_count = ChallengeParticipation.objects.filter(
            challenge=challenge
        ).count()
        
        challenge_data = {
            'id': str(challenge.id),
            'title': str(challenge.title),
            'description': str(challenge.description),
            'target_amount': float(challenge.target_amount),
            'current_amount': float(participation.total_saved),
            'end_date': challenge.end_date.isoformat(),
            'start_date': challenge.start_date.isoformat(),
            'participants_count': participants_count,
            'status': participation.status.lower(),
            'progress': float(participation.progress_percentage),
            'user_contribution': float(participation.total_saved),
            'personal_target': float(participation.personal_target) if participation.personal_target else float(challenge.target_amount),
            'deposits_count': participation.deposits_count,
            'current_streak': participation.current_streak,
            'points_earned': participation.points_earned,
            'challenge_type': str(challenge.challenge_type),
            'category': str(challenge.category),
            'days_remaining': challenge.days_remaining
        }
        challenges.append(challenge_data)
    
    # Si l'utilisateur n'a aucune participation, récupérer les défis publics actifs
    if not challenges:
        public_challenges = SavingsChallenge.objects.filter(
            status='ACTIVE',
            is_public=True
        )[:5]  # Limiter à 5 défis
        
        for challenge in public_challenges:
            participants_count = ChallengeParticipation.objects.filter(
                challenge=challenge
            ).count()
            
            challenge_data = {
                'id': str(challenge.id),
                'title': str(challenge.title),
                'description': str(challenge.description),
                'target_amount': float(challenge.target_amount),
                'current_amount': 0,
                'end_date': challenge.end_date.isoformat(),
                'start_date': challenge.start_date.isoformat(),
                'participants_count': participants_count,
                'status': 'available',
                'progress': 0,
                'user_contribution': 0,
                'personal_target': float(challenge.target_amount),
                'deposits_count': 0,
                'current_streak': 0,
                'points_earned': 0,
                'challenge_type': str(challenge.challenge_type),
                'category': str(challenge.category),
                'days_remaining': challenge.days_remaining
            }
            challenges.append(challenge_data)
    
    return Response({'results': challenges}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_deposits_list(request):
    """Liste des dépôts récents avec données dynamiques de la BD"""
    
    # Pour test temporaire, utiliser l'utilisateur test
    try:
        user = User.objects.get(email="test@xamila.com")
        limit = int(request.GET.get('limit', 5))
        logger.info(f"Deposits request for test user: {user.email}, limit: {limit}")
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Test user not found'}, status=status.HTTP_404_NOT_FOUND)
    
    from .models_savings_challenge import SavingsDeposit, ChallengeParticipation
    
    # Récupérer les dépôts récents de l'utilisateur
    user_deposits = SavingsDeposit.objects.filter(
        participation__user=user
    ).select_related(
        'participation__challenge'
    ).order_by('-created_at')[:limit]
    
    deposits = []
    for deposit in user_deposits:
        deposit_data = {
            'id': str(deposit.id),
            'amount': float(deposit.amount),
            'date': deposit.created_at.date().isoformat(),
            'challenge': deposit.participation.challenge.title,
            'challenge_id': str(deposit.participation.challenge.id),
            'type': deposit.deposit_method.lower(),
            'status': deposit.status.lower(),
            'description': f"Dépôt {deposit.get_deposit_method_display()}",
            'transaction_reference': deposit.transaction_reference,
            'points_awarded': deposit.points_awarded,
            'processed_at': deposit.processed_at.isoformat() if deposit.processed_at else None
        }
        deposits.append(deposit_data)
    
    # Si aucun dépôt trouvé, retourner une liste vide avec un message
    if not deposits:
        logger.info(f"No deposits found for user {user.email}")
    
    return Response({
        'results': deposits,
        'total_count': user_deposits.count() if user_deposits else 0
    }, status=status.HTTP_200_OK)

@method_decorator(login_required, name='dispatch')
class SGIManagerDashboardView(View):
    """Dashboard pour les managers SGI"""
    
    def get(self, request):
        user = request.user
        
        # Données SGI simulées
        sgi_data = {
            'total_clients': 47,
            'active_contracts': 23,
            'pending_contracts': 5,
            'total_aum': 2850000000,  # Assets Under Management
            'performance': 12.8,
            'satisfaction': 94
        }
        
        return JsonResponse(sgi_data)

@method_decorator(login_required, name='dispatch')
class StudentDashboardView(View):
    """Dashboard pour les étudiants STUDENT"""
    
    def get(self, request):
        user = request.user
        
        # Données d'apprentissage simulées
        learning_data = {
            'courses_completed': 12,
            'total_courses': 25,
            'certificates': 4,
            'study_hours': 78,
            'average_score': 85
        }
        
        return JsonResponse(learning_data)

@method_decorator(login_required, name='dispatch')
class InstructorDashboardView(View):
    """Dashboard pour les instructeurs INSTRUCTOR"""
    
    def get(self, request):
        user = request.user
        
        # Données instructeur simulées
        instructor_data = {
            'total_courses': 8,
            'total_students': 156,
            'average_rating': 4.7,
            'total_hours': 42,
            'active_quizzes': 12
        }
        
        return JsonResponse(instructor_data)

@method_decorator(login_required, name='dispatch')
class SupportDashboardView(View):
    """Dashboard pour le support SUPPORT"""
    
    def get(self, request):
        user = request.user
        
        # Données support simulées
        support_data = {
            'total_tickets': 47,
            'open_tickets': 12,
            'resolved_today': 8,
            'average_response_time': 2.3,
            'customer_satisfaction': 94,
            'active_users': 1247
        }
        
        return JsonResponse(support_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_courses_list(request):
    """Liste des cours pour les étudiants"""
    
    # Données simulées des cours
    courses = [
        {
            'id': '1',
            'title': 'Analyse Technique Avancée',
            'description': 'Maîtrisez les outils d\'analyse technique',
            'instructor': 'Dr. Kouame',
            'duration': '4h 30min',
            'progress': 75,
            'status': 'in_progress',
            'certificate': False
        },
        {
            'id': '2',
            'title': 'Gestion de Portefeuille',
            'description': 'Optimisez vos investissements',
            'instructor': 'Prof. Diallo',
            'duration': '6h 15min',
            'progress': 100,
            'status': 'completed',
            'certificate': True
        }
    ]
    
    return Response({'results': courses})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_progress(request):
    """Progression d'apprentissage de l'utilisateur"""
    
    progress_data = {
        'courses_completed': 8,
        'total_courses': 15,
        'certificates': 3,
        'study_hours': 45,
        'average_score': 85
    }
    
    return Response(progress_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_stats(request):
    """Statistiques pour les instructeurs"""
    
    stats_data = {
        'total_courses': 8,
        'total_students': 156,
        'average_rating': 4.7,
        'total_hours': 42
    }
    
    return Response(stats_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_courses_list(request):
    """Liste des cours créés par l'instructeur"""
    
    courses = [
        {
            'id': '1',
            'title': 'Introduction à la Bourse',
            'students_count': 45,
            'completion_rate': 78,
            'average_rating': 4.5,
            'status': 'active'
        },
        {
            'id': '2',
            'title': 'Trading Avancé',
            'students_count': 32,
            'completion_rate': 65,
            'average_rating': 4.8,
            'status': 'active'
        }
    ]
    
    return Response({'results': courses})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def support_tickets_list(request):
    """Liste des tickets de support"""
    
    tickets = [
        {
            'id': '1',
            'title': 'Problème de connexion',
            'description': 'Impossible de se connecter depuis ce matin',
            'priority': 'high',
            'status': 'open',
            'created_at': '2024-08-21T08:30:00Z',
            'assigned_to': 'Support Team'
        },
        {
            'id': '2',
            'title': 'Question sur les frais',
            'description': 'Clarification sur les frais de transaction',
            'priority': 'medium',
            'status': 'in_progress',
            'created_at': '2024-08-20T14:15:00Z',
            'assigned_to': 'Agent Smith'
        }
    ]
    
    return Response({'results': tickets})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """Liste des notifications pour l'utilisateur"""
    
    notifications = [
        {
            'id': '1',
            'title': 'Nouveau challenge disponible',
            'message': 'Un nouveau challenge d\'épargne vient d\'être lancé',
            'type': 'info',
            'created_at': '2024-08-21T10:00:00Z',
            'read': False
        },
        {
            'id': '2',
            'title': 'Cours terminé',
            'message': 'Félicitations ! Vous avez terminé le cours d\'analyse technique',
            'type': 'success',
            'created_at': '2024-08-20T16:30:00Z',
            'read': True
        }
    ]
    
    return Response({'results': notifications})
