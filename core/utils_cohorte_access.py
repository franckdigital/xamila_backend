"""
Utilitaires pour vérifier l'accès aux cohortes et challenges épargne
"""

from .models import Cohorte
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def verifier_acces_challenge_actif(request):
    """
    Vérifie si l'utilisateur a accès au challenge épargne via une cohorte active
    
    Args:
        request: HttpRequest avec l'utilisateur authentifié
        
    Returns:
        tuple: (acces_autorise: bool, message: str)
    """
    try:
        user = request.user
        
        # Vérifier si l'utilisateur est authentifié
        if not user.is_authenticated:
            return False, "Utilisateur non authentifié"
        
        # Initialiser la session si elle n'existe pas (pour les tests)
        if not hasattr(request, 'session'):
            request.session = {}
        
        # Vérifier en session d'abord (cache)
        session_key = f'challenge_access_{user.id}'
        if session_key in request.session:
            cached_access = request.session[session_key]
            if cached_access.get('expires_at', 0) > timezone.now().timestamp():
                return cached_access['access'], cached_access['message']
        
        # Vérifier l'accès via cohortes (relation many-to-many)
        cohortes_actives = user.cohortes.filter(actif=True)
        
        if not cohortes_actives.exists():
            # Vérifier s'il y a des cohortes inactives
            cohortes_inactives = user.cohortes.filter(actif=False)
            if cohortes_inactives.exists():
                message = "Toutes les cohortes de l'utilisateur sont désactivées"
            else:
                message = "Aucune cohorte assignée à l'utilisateur"
            
            # Nettoyer la session
            nettoyer_session_challenge(request, user.id)
            return False, message
        
        # Accès autorisé - mettre en cache avec durée réduite
        cohorte_names = ", ".join([c.nom for c in cohortes_actives])
        access_data = {
            'access': True,
            'message': f"Accès autorisé via cohorte(s): {cohorte_names}",
            'expires_at': (timezone.now() + timedelta(minutes=2)).timestamp()  # Réduit à 2 minutes
        }
        request.session[session_key] = access_data
        
        return True, access_data['message']
        
    except Exception as e:
        error_message = f"Erreur lors de la vérification: {str(e)}"
        return False, error_message

def nettoyer_session_cohorte(request):
    """
    Nettoie les données de session liées aux cohortes
    """
    request.session.pop('challenge_access_activated', None)
    request.session.pop('challenge_cohorte_code', None)

def nettoyer_session_challenge(request, user_id):
    session_key = f'challenge_access_{user_id}'
    request.session.pop(session_key, None)

def decorator_verifier_acces_challenge(view_func):
    """
    Décorateur pour vérifier l'accès au challenge avant d'exécuter une vue
    """
    def wrapper(request, *args, **kwargs):
        from rest_framework.response import Response
        from rest_framework import status
        
        acces_autorise, message = verifier_acces_challenge_actif(request)
        
        if not acces_autorise:
            return Response({
                'error': 'Accès au challenge épargne non autorisé',
                'message': message,
                'code': 'CHALLENGE_ACCESS_DENIED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
