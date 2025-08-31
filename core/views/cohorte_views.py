from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
from ..models import Cohorte


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verifier_code_cohorte(request):
    """
    Vérifie si un code de cohorte est valide pour l'utilisateur connecté
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        
        if not code:
            return Response({
                'valid': False,
                'message': 'Code requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le code avec l'utilisateur connecté
        user = request.user
        is_valid = Cohorte.verifier_code_acces(
            code=code,
            user_email=user.email,
            user_id=user.id
        )
        
        if is_valid:
            # Récupérer les informations de la cohorte
            cohorte = Cohorte.objects.get(
                code=code,
                email_utilisateur=user.email,
                user_id=user.id,
                actif=True
            )
            
            return Response({
                'valid': True,
                'message': 'Code valide',
                'cohorte': {
                    'id': str(cohorte.id),
                    'nom': cohorte.nom,
                    'mois': cohorte.mois,
                    'annee': cohorte.annee,
                    'code': cohorte.code
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False,
                'message': 'Code invalide ou non autorisé pour cet utilisateur'
            }, status=status.HTTP_403_FORBIDDEN)
            
    except json.JSONDecodeError:
        return Response({
            'valid': False,
            'message': 'Format de données invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'valid': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_cohortes(request):
    """
    Récupère toutes les cohortes de l'utilisateur connecté
    """
    try:
        user = request.user
        cohortes = Cohorte.objects.filter(
            user=user,
            actif=True
        ).order_by('-annee', '-mois')
        
        cohortes_data = []
        for cohorte in cohortes:
            mois_nom = dict(Cohorte.MOIS_CHOICES)[cohorte.mois]
            cohortes_data.append({
                'id': str(cohorte.id),
                'code': cohorte.code,
                'nom': cohorte.nom,
                'mois': cohorte.mois,
                'mois_nom': mois_nom,
                'annee': cohorte.annee,
                'created_at': cohorte.created_at.isoformat()
            })
        
        return Response({
            'cohortes': cohortes_data,
            'count': len(cohortes_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activer_acces_challenge(request):
    """
    Active l'accès au Challenge Épargne pour l'utilisateur connecté
    après vérification du code cohorte
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        
        if not code:
            return Response({
                'success': False,
                'message': 'Code requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Vérifier le code
        is_valid = Cohorte.verifier_code_acces(
            code=code,
            user_email=user.email,
            user_id=user.id
        )
        
        if is_valid:
            # Marquer l'accès comme activé (peut être stocké en session ou dans le profil utilisateur)
            request.session['challenge_access_activated'] = True
            request.session['challenge_cohorte_code'] = code
            
            cohorte = Cohorte.objects.get(
                code=code,
                email_utilisateur=user.email,
                user_id=user.id,
                actif=True
            )
            
            return Response({
                'success': True,
                'message': 'Accès au Challenge Épargne activé',
                'cohorte': {
                    'nom': cohorte.nom,
                    'mois': cohorte.mois,
                    'annee': cohorte.annee
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Code invalide ou non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Format de données invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
