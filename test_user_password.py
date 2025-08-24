#!/usr/bin/env python
"""
Test pour vérifier et corriger le mot de passe de l'utilisateur test
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import User

def test_and_fix_user_password():
    """Tester et corriger le mot de passe de l'utilisateur test"""
    
    print("=== TEST ET CORRECTION MOT DE PASSE ===")
    
    try:
        # Récupérer l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        print(f"Utilisateur trouvé: {user.email}")
        print(f"Is active: {user.is_active}")
        print(f"Has usable password: {user.has_usable_password()}")
        
        # Tester l'authentification avec différents mots de passe
        passwords_to_test = [
            "TestPassword123!",
            "testpassword123",
            "password123",
            "test123"
        ]
        
        print("\n=== TEST AUTHENTIFICATION ===")
        for password in passwords_to_test:
            auth_user = authenticate(email="test@xamila.com", password=password)
            if auth_user:
                print(f"OK Authentification réussie avec: {password}")
                return
            else:
                print(f"ECHEC avec: {password}")
        
        # Si aucun mot de passe ne fonctionne, en définir un nouveau
        print("\n=== CORRECTION MOT DE PASSE ===")
        new_password = "TestPassword123!"
        user.set_password(new_password)
        user.save()
        print(f"Nouveau mot de passe défini: {new_password}")
        
        # Tester le nouveau mot de passe
        auth_user = authenticate(email="test@xamila.com", password=new_password)
        if auth_user:
            print(f"OK Authentification réussie avec le nouveau mot de passe")
        else:
            print(f"ECHEC avec le nouveau mot de passe")
        
    except User.DoesNotExist:
        print("ERREUR: Utilisateur test@xamila.com non trouvé")
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_and_fix_user_password()
