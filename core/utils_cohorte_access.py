"""
Utilitaires pour vérifier l'accès aux cohortes et challenges épargne
"""

from .models import Cohorte
from django.contrib.auth import get_user_model

User = get_user_model()

def verifier_acces_challenge_actif(request):
    """
    Vérifie si l'utilisateur a toujours accès au challenge épargne
    en s'assurant que sa cohorte est toujours active
    """
    try:
        # Vérifier si l'accès est activé en session
        if not request.session.get('challenge_access_activated', False):
            return False, "Accès au challenge non activé"
        
        # Récupérer le code de cohorte depuis la session
        cohorte_code = request.session.get('challenge_cohorte_code')
        if not cohorte_code:
            return False, "Code de cohorte non trouvé en session"
        
        user = request.user
        if not user.is_authenticated:
            return False, "Utilisateur non authentifié"
        
        # Vérifier que la cohorte existe et est toujours active
        try:
            cohorte = Cohorte.objects.get(
                code=cohorte_code,
                email_utilisateur=user.email,
                user_id=user.id,
                actif=True  # Vérification cruciale du statut actif
            )
            return True, f"Accès autorisé pour la cohorte {cohorte.nom}"
            
        except Cohorte.DoesNotExist:
            # La cohorte n'existe plus ou a été désactivée
            # Nettoyer la session
            request.session.pop('challenge_access_activated', None)
            request.session.pop('challenge_cohorte_code', None)
            return False, "Cohorte désactivée ou non trouvée"
            
    except Exception as e:
        return False, f"Erreur lors de la vérification: {str(e)}"

def nettoyer_session_cohorte(request):
    """
    Nettoie les données de session liées aux cohortes
    """
    request.session.pop('challenge_access_activated', None)
    request.session.pop('challenge_cohorte_code', None)

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
