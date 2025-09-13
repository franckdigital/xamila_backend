"""
Vues pour la gestion de l'accès aux cohortes
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Cohorte
from .utils_cohorte_access import verifier_acces_challenge_actif
from .serializers import CohorteSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_cohort_access(request):
    """
    Vérifie si l'utilisateur a accès au challenge épargne via une cohorte active
    """
    try:
        user = request.user
        logger.info(f"Vérification accès cohorte pour utilisateur: {user.email}")
        
        # Utiliser la fonction utilitaire existante
        acces_autorise, message = verifier_acces_challenge_actif(request)
        
        # Récupérer les cohortes de l'utilisateur
        user_cohorts = user.cohortes.all()
        cohorts_data = []
        
        for cohorte in user_cohorts:
            cohorts_data.append({
                'id': str(cohorte.id),
                'nom': cohorte.nom,
                'actif': cohorte.actif,
                'mois': cohorte.mois,
                'annee': cohorte.annee
            })
        
        response_data = {
            'access_authorized': acces_autorise,
            'message': message,
            'user_cohorts': cohorts_data
        }
        
        logger.info(f"Résultat vérification accès: {acces_autorise} - {message}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification d'accès cohorte: {str(e)}")
        return Response({
            'access_authorized': False,
            'message': f'Erreur lors de la vérification: {str(e)}',
            'user_cohorts': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_cohort_with_code(request):
    """
    Permet à un utilisateur de rejoindre une cohorte avec un code
    """
    try:
        user = request.user
        code_cohorte = request.data.get('code_cohorte', '').strip().upper()
        
        if not code_cohorte:
            return Response({
                'success': False,
                'message': 'Code cohorte requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Tentative d'adhésion cohorte pour {user.email} avec code: {code_cohorte}")
        
        # Rechercher la cohorte par code
        try:
            cohorte = Cohorte.objects.get(code__iexact=code_cohorte)
        except Cohorte.DoesNotExist:
            logger.warning(f"Code cohorte invalide: {code_cohorte}")
            return Response({
                'success': False,
                'message': 'Code cohorte invalide ou cohorte introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si la cohorte est active
        if not cohorte.actif:
            logger.warning(f"Tentative d'adhésion à cohorte inactive: {cohorte.nom}")
            return Response({
                'success': False,
                'message': 'Cette cohorte n\'est pas active actuellement'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur est déjà dans cette cohorte
        if user.cohortes.filter(id=cohorte.id).exists():
            # Nettoyer le cache de session pour forcer une nouvelle vérification
            session_key = f'challenge_access_{user.id}'
            if session_key in request.session:
                del request.session[session_key]
            
            return Response({
                'success': True,
                'message': f'Vous êtes déjà membre de la cohorte {cohorte.nom}',
                'cohorte': {
                    'id': str(cohorte.id),
                    'nom': cohorte.nom,
                    'actif': cohorte.actif,
                    'mois': cohorte.mois,
                    'annee': cohorte.annee
                }
            }, status=status.HTTP_200_OK)
        
        # Ajouter l'utilisateur à la cohorte
        with transaction.atomic():
            user.cohortes.add(cohorte)
            
            # Mettre à jour l'email utilisateur si nécessaire
            if cohorte.email_utilisateur != user.email:
                cohorte.email_utilisateur = user.email
                cohorte.save()
        
        logger.info(f"Utilisateur {user.email} ajouté avec succès à la cohorte {cohorte.nom}")
        
        # Nettoyer le cache de session pour forcer une nouvelle vérification
        session_key = f'challenge_access_{user.id}'
        if session_key in request.session:
            del request.session[session_key]
        
        return Response({
            'success': True,
            'message': f'Félicitations ! Vous avez rejoint la cohorte {cohorte.nom}',
            'cohorte': {
                'id': str(cohorte.id),
                'nom': cohorte.nom,
                'actif': cohorte.actif,
                'mois': cohorte.mois,
                'annee': cohorte.annee
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'adhésion à la cohorte: {str(e)}")
        return Response({
            'success': False,
            'message': 'Erreur interne lors de l\'adhésion à la cohorte'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cohorts(request):
    """
    Récupère les cohortes de l'utilisateur connecté
    """
    try:
        user = request.user
        cohorts = user.cohortes.all()
        
        cohorts_data = []
        for cohorte in cohorts:
            cohorts_data.append({
                'id': str(cohorte.id),
                'nom': cohorte.nom,
                'actif': cohorte.actif,
                'mois': cohorte.mois,
                'annee': cohorte.annee,
                'created_at': cohorte.created_at.isoformat() if cohorte.created_at else None
            })
        
        return Response({
            'cohorts': cohorts_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cohortes utilisateur: {str(e)}")
        return Response({
            'cohorts': [],
            'error': 'Erreur lors de la récupération des cohortes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
