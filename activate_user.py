#!/usr/bin/env python
"""
Script pour activer manuellement un compte utilisateur
Usage: python activate_user.py <email>
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User

def activate_user(email):
    """Active un compte utilisateur par email"""
    try:
        user = User.objects.get(email=email)
        
        print(f"Utilisateur trouvé: {user.email}")
        print(f"Statut actuel: {'Activé' if user.is_active else 'Non activé'}")
        print(f"Email vérifié: {'Oui' if user.email_verified else 'Non'}")
        
        if not user.is_active:
            user.is_active = True
            user.email_verified = True
            user.save()
            print(f"✅ Compte activé avec succès pour {email}")
        else:
            print(f"ℹ️  Le compte {email} est déjà activé")
            
        return True
        
    except User.DoesNotExist:
        print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'activation: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python activate_user.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = activate_user(email)
    sys.exit(0 if success else 1)
