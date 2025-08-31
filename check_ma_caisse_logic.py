#!/usr/bin/env python
"""
Script pour vérifier la logique Ma Caisse quand il n'y a pas d'objectifs
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import SavingsGoal

def check_ma_caisse_logic():
    """
    Vérifie ce qui se passe quand il n'y a pas d'objectifs
    """
    print("=== VÉRIFICATION LOGIQUE MA CAISSE ===")
    
    # Vérifier les utilisateurs
    users = User.objects.all()
    print(f"Utilisateurs dans la DB: {users.count()}")
    
    for user in users[:3]:
        print(f"\nUtilisateur: {user.email}")
        
        # Vérifier les objectifs de cet utilisateur
        objectifs = SavingsGoal.objects.filter(user=user)
        print(f"  Objectifs: {objectifs.count()}")
        
        if objectifs.exists():
            premier_objectif = objectifs.first()
            print(f"  Premier objectif: {premier_objectif.title}")
            print(f"  Date activation: {premier_objectif.date_activation_caisse}")
            print(f"  Activé: {premier_objectif.is_caisse_activated}")
        else:
            print("  Aucun objectif trouvé")
    
    # Vérifier la logique de l'API
    print(f"\n=== SIMULATION API ===")
    
    # Simuler ce que fait l'API views_ma_caisse.py
    test_user = users.first() if users.exists() else None
    
    if test_user:
        objectifs = SavingsGoal.objects.filter(user=test_user)
        
        if not objectifs.exists():
            print(f"Utilisateur {test_user.email}: Aucun objectif")
            print("L'API retournerait probablement une erreur ou caisse_activated=True par défaut")
        else:
            premier_objectif = objectifs.first()
            is_activated = premier_objectif.is_caisse_activated
            print(f"Utilisateur {test_user.email}: caisse_activated={is_activated}")

if __name__ == '__main__':
    check_ma_caisse_logic()
