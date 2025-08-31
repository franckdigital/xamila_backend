#!/usr/bin/env python
"""
Script pour déboguer l'activation de Ma Caisse
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal
from core.models import User

def debug_ma_caisse():
    """
    Debug l'activation de Ma Caisse pour tous les utilisateurs
    """
    print("=== DEBUG MA CAISSE ACTIVATION ===")
    
    # Récupérer tous les objectifs d'épargne
    objectifs = SavingsGoal.objects.all().order_by('created_at')
    
    print(f"Total objectifs trouvés: {objectifs.count()}")
    print()
    
    today = date.today()
    
    for objectif in objectifs:
        print(f"Objectif: {objectif.title}")
        print(f"  - ID: {objectif.id}")
        print(f"  - Utilisateur: {objectif.user.email}")
        print(f"  - Créé le: {objectif.created_at.date()}")
        print(f"  - Date activation caisse: {objectif.date_activation_caisse}")
        print(f"  - Is caisse activated: {objectif.is_caisse_activated}")
        print(f"  - Jours depuis création: {(today - objectif.created_at.date()).days}")
        
        if objectif.date_activation_caisse:
            days_remaining = (objectif.date_activation_caisse - today).days
            print(f"  - Jours restants: {days_remaining}")
        
        print("  ---")
    
    # Tester l'API
    print("\n=== TEST API MA CAISSE ===")
    
    # Simuler une requête API pour chaque utilisateur
    users_with_goals = User.objects.filter(savings_goals__isnull=False).distinct()
    
    for user in users_with_goals:
        print(f"\nUtilisateur: {user.email}")
        
        # Simuler la logique de l'API verifier_activation_caisse
        user_objectifs = SavingsGoal.objects.filter(
            user=user,
            status='ACTIVE'
        ).order_by('created_at')
        
        if user_objectifs.exists():
            premier_objectif = user_objectifs.first()
            is_activated = premier_objectif.is_caisse_activated
            
            print(f"  - Premier objectif: {premier_objectif.title}")
            print(f"  - Date activation: {premier_objectif.date_activation_caisse}")
            print(f"  - Ma Caisse activée: {is_activated}")
            
            if premier_objectif.date_activation_caisse and not is_activated:
                days_remaining = (premier_objectif.date_activation_caisse - today).days
                print(f"  - Jours restants: {days_remaining}")
        else:
            print("  - Aucun objectif actif")

if __name__ == '__main__':
    debug_ma_caisse()
