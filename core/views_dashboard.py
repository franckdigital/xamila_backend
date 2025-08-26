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
from .models_dashboard import UserInvestment, UserSavingsProgress, DashboardTransaction, UserDashboardStats
from .models_savings_challenge import SavingsChallenge
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_dashboard_stats(request):
    """Statistiques du dashboard customer avec données réelles de la BD"""
    
    user = request.user
    logger.info(f"Dashboard stats request for user: {user.email}")
    
    try:
        # Récupérer ou créer les stats du dashboard
        dashboard_stats, created = UserDashboardStats.objects.get_or_create(
            user=user,
            defaults={
                'total_portfolio_value': 0,
                'total_invested_amount': 0,
                'global_performance_percentage': 0,
                'current_month_savings': 0,
                'savings_rank': 0,
                'total_savings': 0
            }
        )
        
        # Rafraîchir les statistiques si nécessaire (plus de 1h)
        from django.utils import timezone
        if created or (timezone.now() - dashboard_stats.last_updated).seconds > 3600:
            dashboard_stats.refresh_stats()
        
        # Calculer les données supplémentaires
        from datetime import datetime
        current_month = datetime.now().replace(day=1)
        
        # Épargne du mois actuel
        monthly_savings = DashboardTransaction.objects.filter(
            user=user,
            transaction_type='SAVINGS',
            status='CONFIRMED',
            created_at__gte=current_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Rang dans le challenge actuel
        active_challenge = SavingsChallenge.objects.filter(status='ACTIVE').first()
        savings_rank = 0
        if active_challenge:
            user_progress = UserSavingsProgress.objects.filter(
                user=user, 
                challenge=active_challenge
            ).first()
            if user_progress:
                savings_rank = user_progress.rank
        
        stats_data = {
            'user_id': str(user.id),
            'user_name': user.get_full_name() or user.email,
            'user_role': user.role,
            'total_portfolio_value': float(dashboard_stats.total_portfolio_value),
            'total_invested_amount': float(dashboard_stats.total_invested_amount),
            'global_performance_percentage': float(dashboard_stats.global_performance_percentage),
            'current_month_savings': float(monthly_savings),
            'savings_rank': savings_rank or dashboard_stats.savings_rank,
            'total_savings': float(dashboard_stats.total_savings),
            'last_updated': dashboard_stats.last_updated.isoformat()
        }
        
        logger.info(f"Returning dashboard stats for {user.email}")
        return Response(stats_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats for {user.email}: {str(e)}")
        return Response({'error': 'Unable to fetch dashboard stats'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_investments_list(request):
    """Liste des investissements SGI de l'utilisateur"""
    
    user = request.user
    logger.info(f"Investments request for user: {user.email}")
    
    try:
        investments = UserInvestment.objects.filter(
            user=user,
            is_active=True
        ).select_related('sgi').order_by('-created_at')
        
        investments_data = []
        for investment in investments:
            investment_data = {
                'id': str(investment.id),
                'sgi_name': investment.sgi.name if investment.sgi else 'SGI Non définie',
                'sgi_type': investment.sgi.investment_type if investment.sgi else 'N/A',
                'invested_amount': float(investment.invested_amount),
                'current_value': float(investment.current_value),
                'performance_percentage': float(investment.performance_percentage),
                'profit_loss': float(investment.profit_loss),
                'purchase_date': investment.purchase_date.isoformat(),
                'is_active': investment.is_active
            }
            investments_data.append(investment_data)
        
        return Response({'results': investments_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching investments for {user.email}: {str(e)}")
        return Response({'error': 'Unable to fetch investments'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_savings_challenges(request):
    """Challenges d'épargne de l'utilisateur avec progression"""
    
    user = request.user
    logger.info(f"Savings challenges request for user: {user.email}")
    
    try:
        # Récupérer les progressions de l'utilisateur
        user_progress = UserSavingsProgress.objects.filter(
            user=user
        ).select_related('challenge').order_by('-created_at')
        
        challenges_data = []
        for progress in user_progress:
            challenge = progress.challenge
            
            # Calculer le classement global
            total_participants = UserSavingsProgress.objects.filter(
                challenge=challenge
            ).count()
            
            # Top 3 du classement
            leaderboard = UserSavingsProgress.objects.filter(
                challenge=challenge
            ).order_by('-current_amount')[:3]
            
            leaderboard_data = []
            for i, leader in enumerate(leaderboard, 1):
                leaderboard_data.append({
                    'rank': i,
                    'name': leader.user.get_full_name() or leader.user.username,
                    'amount': float(leader.current_amount)
                })
            
            challenge_data = {
                'id': str(challenge.id),
                'title': challenge.title,
                'description': challenge.description,
                'target_amount': float(challenge.target_amount),
                'current_amount': float(progress.current_amount),
                'progress_percentage': float(progress.progress_percentage),
                'streak_days': progress.streak_days,
                'badges_earned': progress.badges_earned,
                'rank': progress.rank,
                'total_participants': total_participants,
                'leaderboard': leaderboard_data,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'is_active': challenge.is_active,
                'last_saving_date': progress.last_saving_date.isoformat() if progress.last_saving_date else None
            }
            challenges_data.append(challenge_data)
        
        return Response({'results': challenges_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching savings challenges for {user.email}: {str(e)}")
        return Response({'error': 'Unable to fetch savings challenges'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_transactions_list(request):
    """Historique des transactions de l'utilisateur"""
    
    user = request.user
    limit = int(request.GET.get('limit', 10))
    logger.info(f"Transactions request for user: {user.email}, limit: {limit}")
    
    try:
        transactions = DashboardTransaction.objects.filter(
            user=user
        ).select_related('sgi', 'investment', 'savings_challenge').order_by('-created_at')[:limit]
        
        transactions_data = []
        for transaction in transactions:
            # Déterminer l'icône et la couleur selon le type
            icon_color_map = {
                'INVESTMENT': {'icon': 'ArrowUpward', 'color': '#4caf50'},
                'WITHDRAWAL': {'icon': 'ArrowDownward', 'color': '#f44336'},
                'SAVINGS': {'icon': 'Savings', 'color': '#ff9800'},
                'DIVIDEND': {'icon': 'TrendingUp', 'color': '#2196f3'},
                'FEE': {'icon': 'Remove', 'color': '#9e9e9e'}
            }
            
            icon_info = icon_color_map.get(transaction.transaction_type, {'icon': 'AccountBalance', 'color': '#1976d2'})
            
            # Déterminer la description contextuelle
            context_name = 'N/A'
            if transaction.sgi:
                context_name = transaction.sgi.name
            elif transaction.savings_challenge:
                context_name = transaction.savings_challenge.title
            
            transaction_data = {
                'id': str(transaction.id),
                'type': transaction.get_transaction_type_display(),
                'amount': f"{'+' if transaction.transaction_type in ['INVESTMENT', 'SAVINGS', 'DIVIDEND'] else '-'}{float(abs(transaction.amount)):,.0f} FCFA",
                'amount_value': float(transaction.amount),
                'date': transaction.created_at.strftime('%d %b %Y'),
                'status': transaction.get_status_display(),
                'description': transaction.description,
                'context_name': context_name,
                'reference_id': transaction.reference_id,
                'icon': icon_info['icon'],
                'color': icon_info['color'],
                'processed_at': transaction.processed_at.isoformat() if transaction.processed_at else None
            }
            transactions_data.append(transaction_data)
        
        return Response({'results': transactions_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching transactions for {user.email}: {str(e)}")
        return Response({'error': 'Unable to fetch transactions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_challenges_list(request):
    """Liste des défis d'épargne avec données dynamiques de la BD"""
    
    # Utiliser l'utilisateur authentifié
    user = request.user
    logger.info(f"Challenges request for user: {user.email}")
    
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
    
    # Utiliser l'utilisateur authentifié
    user = request.user
    limit = int(request.GET.get('limit', 5))
    logger.info(f"Deposits request for user: {user.email}, limit: {limit}")
    
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
