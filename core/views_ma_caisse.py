"""
API endpoints pour la gestion de Ma Caisse
Activation automatique 21 jours après création d'objectif d'épargne
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from .models_savings_challenge import SavingsGoal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verifier_activation_caisse(request):
    """
    Vérifie si Ma Caisse est activée pour l'utilisateur connecté
    Basé sur les objectifs d'épargne créés il y a au moins 21 jours
    """
    try:
        user = request.user
        
        # Chercher les objectifs d'épargne de l'utilisateur
        objectifs = SavingsGoal.objects.filter(
            user=user,
            status='ACTIVE'
        ).order_by('created_at')
        
        if not objectifs.exists():
            return Response({
                'caisse_activated': False,
                'message': 'Aucun objectif d\'épargne trouvé',
                'days_remaining': None,
                'activation_date': None
            })
        
        # Prendre le premier objectif créé
        premier_objectif = objectifs.first()
        
        # Vérifier si Ma Caisse est activée
        is_activated = premier_objectif.is_caisse_activated
        
        if is_activated:
            return Response({
                'caisse_activated': True,
                'message': 'Ma Caisse est activée',
                'activation_date': premier_objectif.date_activation_caisse.isoformat(),
                'objectif_id': str(premier_objectif.id),
                'objectif_title': premier_objectif.title
            })
        else:
            # Calculer les jours restants
            days_remaining = (premier_objectif.date_activation_caisse - date.today()).days
            
            return Response({
                'caisse_activated': False,
                'message': f'Ma Caisse sera activée dans {days_remaining} jour(s)',
                'days_remaining': days_remaining,
                'activation_date': premier_objectif.date_activation_caisse.isoformat(),
                'objectif_id': str(premier_objectif.id),
                'objectif_title': premier_objectif.title
            })
            
    except Exception as e:
        return Response({
            'caisse_activated': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statut_objectifs_epargne(request):
    """
    Retourne le statut de tous les objectifs d'épargne de l'utilisateur
    avec leurs dates d'activation Ma Caisse
    """
    try:
        user = request.user
        
        objectifs = SavingsGoal.objects.filter(user=user).order_by('-created_at')
        
        objectifs_data = []
        for objectif in objectifs:
            objectifs_data.append({
                'id': str(objectif.id),
                'title': objectif.title,
                'target_amount': float(objectif.target_amount),
                'current_amount': float(objectif.current_amount),
                'progress_percentage': objectif.progress_percentage,
                'status': objectif.status,
                'created_at': objectif.created_at.isoformat(),
                'date_activation_caisse': objectif.date_activation_caisse.isoformat() if objectif.date_activation_caisse else None,
                'is_caisse_activated': objectif.is_caisse_activated,
                'days_until_activation': (objectif.date_activation_caisse - date.today()).days if objectif.date_activation_caisse and not objectif.is_caisse_activated else 0
            })
        
        return Response({
            'success': True,
            'objectifs': objectifs_data,
            'total_objectifs': len(objectifs_data)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
