"""
Vues pour la gestion des objectifs d'épargne mensuels
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

def get_french_month_year():
    """Retourne le mois et l'année en français"""
    months_fr = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    now = timezone.now()
    return f"{months_fr[now.month]} {now.year}"

from .models import User
from .serializers import UserSerializer


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def monthly_savings_goal(request):
    """
    GET: Récupère l'objectif d'épargne mensuel de l'utilisateur
    PUT: Met à jour l'objectif d'épargne mensuel de l'utilisateur
    """
    user = request.user
    
    if request.method == 'GET':
        # Vérifier si l'objectif doit être remis à zéro (nouveau mois)
        if user.monthly_goal_set_date:
            current_month = timezone.now().month
            current_year = timezone.now().year
            goal_month = user.monthly_goal_set_date.month
            goal_year = user.monthly_goal_set_date.year
            
            # Si on est dans un nouveau mois, remettre l'objectif à zéro
            if current_month != goal_month or current_year != goal_year:
                user.monthly_savings_goal = Decimal('0.00')
                user.monthly_goal_set_date = None
                user.save()
        
        return Response({
            'monthly_savings_goal': float(user.monthly_savings_goal),
            'goal_set_date': user.monthly_goal_set_date.isoformat() if user.monthly_goal_set_date else None,
            'current_month': timezone.now().strftime('%B %Y')
        })
    
    elif request.method == 'PUT':
        try:
            goal_amount = request.data.get('monthly_savings_goal')
            
            if goal_amount is None:
                return Response({
                    'error': 'Le montant de l\'objectif est requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            goal_amount = Decimal(str(goal_amount))
            
            if goal_amount < 0:
                return Response({
                    'error': 'L\'objectif ne peut pas être négatif'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.monthly_savings_goal = goal_amount
            user.monthly_goal_set_date = timezone.now()
            user.save()
            
            return Response({
                'monthly_savings_goal': float(user.monthly_savings_goal),
                'goal_set_date': user.monthly_goal_set_date.isoformat(),
                'current_month': timezone.now().strftime('%B %Y'),
                'message': 'Objectif mensuel mis à jour avec succès'
            })
            
        except (ValueError, TypeError) as e:
            return Response({
                'error': 'Montant invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la mise à jour: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_savings_progress(request):
    """
    Calcule la progression de l'utilisateur vers son objectif mensuel
    """
    user = request.user
    
    # Calculer les dépôts du mois actuel
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
    
    # Importer ici pour éviter les imports circulaires
    from .models_savings_challenge import SavingsDeposit, ChallengeParticipation
    
    # Calculer le total des dépôts du mois actuel depuis les dépôts d'épargne
    from django.db import models
    from .models_savings_challenge import SavingsDeposit
    
    monthly_deposits = SavingsDeposit.objects.filter(
        participation__user=user,
        status='CONFIRMED',
        created_at__gte=current_month_start,
        created_at__lt=next_month_start
    ).aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Calculer le pourcentage de progression
    progress_percentage = 0
    if user.monthly_savings_goal > 0:
        progress_percentage = min(100, (monthly_deposits / user.monthly_savings_goal) * 100)
    
    return Response({
        'monthly_goal': float(user.monthly_savings_goal),
        'current_savings': float(monthly_deposits),
        'progress_percentage': round(float(progress_percentage), 2),
        'remaining_amount': float(max(0, user.monthly_savings_goal - monthly_deposits)),
        'current_month': get_french_month_year(),
        'days_remaining': (next_month_start - timezone.now()).days
    })
