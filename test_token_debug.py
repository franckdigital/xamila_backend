#!/usr/bin/env python
"""
Script pour déboguer le problème de validation des tokens JWT
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from django.test import RequestFactory
from django.conf import settings

def debug_token_validation():
    """Déboguer la validation des tokens JWT"""
    
    print("=== DEBUG TOKEN JWT ===")
    
    # 1. Récupérer l'utilisateur
    try:
        user = User.objects.get(email="test@xamila.com")
        print(f"OK Utilisateur trouve: {user.email}")
        print(f"  - ID: {user.id}")
        print(f"  - Type ID: {type(user.id)}")
        print(f"  - Actif: {user.is_active}")
    except User.DoesNotExist:
        print("ERROR Utilisateur non trouve")
        return
    
    # 2. Générer un token
    print("\n=== GENERATION TOKEN ===")
    try:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"OK Token genere")
        print(f"  - Refresh: {str(refresh)[:50]}...")
        print(f"  - Access: {access_token[:50]}...")
        
        # Décoder le token pour voir son contenu
        import jwt
        from django.conf import settings as django_settings
        decoded = jwt.decode(access_token, django_settings.SECRET_KEY, algorithms=['HS256'])
        print(f"  - Payload: {decoded}")
        
    except Exception as e:
        print(f"ERROR Generation token: {str(e)}")
        return
    
    # 3. Tester la validation du token
    print("\n=== VALIDATION TOKEN ===")
    try:
        # Créer une requête factice avec le token
        factory = RequestFactory()
        request = factory.get('/test/', HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Utiliser l'authentificateur JWT
        jwt_auth = JWTAuthentication()
        
        # Tenter d'authentifier
        auth_result = jwt_auth.authenticate(request)
        
        if auth_result:
            authenticated_user, validated_token = auth_result
            print(f"OK Token valide")
            print(f"  - Utilisateur authentifie: {authenticated_user.email}")
            print(f"  - Token valide: {type(validated_token)}")
        else:
            print("ERROR Token invalide - authenticate() retourne None")
            
    except Exception as e:
        print(f"ERROR Validation token: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    # 4. Vérifier les paramètres JWT
    print("\n=== PARAMETRES JWT ===")
    from django.conf import settings
    jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
    print(f"  - SIGNING_KEY: {jwt_settings.get('SIGNING_KEY', 'NOT_SET')[:20]}...")
    print(f"  - ALGORITHM: {jwt_settings.get('ALGORITHM')}")
    print(f"  - USER_ID_FIELD: {jwt_settings.get('USER_ID_FIELD')}")
    print(f"  - USER_ID_CLAIM: {jwt_settings.get('USER_ID_CLAIM')}")
    print(f"  - TOKEN_USER_CLASS: {jwt_settings.get('TOKEN_USER_CLASS')}")
    
    # 5. Test direct avec les paramètres
    print("\n=== TEST DIRECT ===")
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        # Créer un token d'accès
        access = AccessToken.for_user(user)
        print(f"OK AccessToken cree: {str(access)[:50]}...")
        
        # Valider le token
        try:
            validated = AccessToken(str(access))
            print(f"OK Token AccessToken valide")
            print(f"  - User ID dans token: {validated.get('user_id')}")
            print(f"  - User ID reel: {user.id}")
        except (InvalidToken, TokenError) as te:
            print(f"ERROR Token AccessToken invalide: {str(te)}")
            
    except Exception as e:
        print(f"ERROR Test direct: {str(e)}")

if __name__ == "__main__":
    debug_token_validation()
