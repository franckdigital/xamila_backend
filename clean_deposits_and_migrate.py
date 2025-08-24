#!/usr/bin/env python
"""
Script pour nettoyer les dépôts existants et faire la migration
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsDeposit

def clean_deposits():
    """Supprime tous les dépôts existants"""
    
    print("=== NETTOYAGE DES DEPOTS ===")
    
    try:
        # Supprimer tous les dépôts
        count = SavingsDeposit.objects.count()
        SavingsDeposit.objects.all().delete()
        print(f"OK {count} dépôts supprimés")
        
        print("\n=== NETTOYAGE TERMINÉ ===")
        print("Vous pouvez maintenant faire la migration:")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_deposits()
