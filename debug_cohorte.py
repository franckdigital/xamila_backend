#!/usr/bin/env python
"""
Script pour déboguer les cohortes utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_cohorte import Cohorte
from core.models import User

def debug_cohortes():
    """
    Debug les cohortes pour tous les utilisateurs
    """
    print("=== DEBUG COHORTES ===")
    
    # Récupérer toutes les cohortes
    cohortes = Cohorte.objects.all()
    
    print(f"Total cohortes trouvées: {cohortes.count()}")
    print()
    
    for cohorte in cohortes:
        print(f"Cohorte: {cohorte.nom}")
        print(f"  - Code: {cohorte.code}")
        print(f"  - Utilisateur: {cohorte.utilisateur.email}")
        print(f"  - Mois: {cohorte.mois}")
        print(f"  - Année: {cohorte.annee}")
        print("  ---")
    
    # Tester l'API getMesCohortes pour chaque utilisateur
    print("\n=== TEST API COHORTES ===")
    
    users_with_cohortes = User.objects.filter(cohortes__isnull=False).distinct()
    
    print(f"Utilisateurs avec cohortes: {users_with_cohortes.count()}")
    
    for user in users_with_cohortes:
        print(f"\nUtilisateur: {user.email}")
        
        user_cohortes = Cohorte.objects.filter(utilisateur=user)
        
        print(f"  - Nombre de cohortes: {user_cohortes.count()}")
        
        for cohorte in user_cohortes:
            print(f"  - Code: {cohorte.code}")
    
    # Vérifier tous les utilisateurs
    print(f"\n=== TOUS LES UTILISATEURS ===")
    all_users = User.objects.all()
    
    for user in all_users:
        user_cohortes = Cohorte.objects.filter(utilisateur=user)
        print(f"{user.email}: {user_cohortes.count()} cohorte(s)")

if __name__ == '__main__':
    debug_cohortes()
