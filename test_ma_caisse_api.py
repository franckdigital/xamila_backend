#!/usr/bin/env python
"""
Script pour tester l'API Ma Caisse directement
"""

import os
import sys
import django
import requests
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal
from core.models import User

def test_ma_caisse_api():
    """
    Test l'API Ma Caisse pour voir ce qu'elle retourne
    """
    print("=== TEST API MA CAISSE ===")
    
    # Tester avec un utilisateur spécifique
    try:
        user = User.objects.filter(email__icontains='demo').first()
        if not user:
            user = User.objects.first()
        
        if user:
            print(f"Test avec utilisateur: {user.email}")
            
            # Simuler la logique de l'API verifier_activation_caisse
            objectifs = SavingsGoal.objects.filter(
                user=user,
                status='ACTIVE'
            ).order_by('created_at')
            
            print(f"Objectifs actifs trouvés: {objectifs.count()}")
            
            if objectifs.exists():
                premier_objectif = objectifs.first()
                
                print(f"Premier objectif: {premier_objectif.title}")
                print(f"Créé le: {premier_objectif.created_at.date()}")
                print(f"Date activation caisse: {premier_objectif.date_activation_caisse}")
                
                # Tester la propriété is_caisse_activated
                is_activated = premier_objectif.is_caisse_activated
                print(f"is_caisse_activated: {is_activated}")
                
                # Calculer manuellement
                today = date.today()
                if premier_objectif.date_activation_caisse:
                    manual_check = today >= premier_objectif.date_activation_caisse
                    print(f"Vérification manuelle (today >= activation_date): {manual_check}")
                    print(f"Aujourd'hui: {today}")
                    print(f"Date activation: {premier_objectif.date_activation_caisse}")
                    
                    days_diff = (premier_objectif.date_activation_caisse - today).days
                    print(f"Jours restants: {days_diff}")
                
                # Vérifier le code de la propriété is_caisse_activated
                print("\n=== VERIFICATION PROPRIETE ===")
                print("Code de la propriété is_caisse_activated:")
                print("@property")
                print("def is_caisse_activated(self):")
                print("    if not self.date_activation_caisse:")
                print("        return False")
                print("    return date.today() >= self.date_activation_caisse")
                
            else:
                print("Aucun objectif actif trouvé")
        
        # Lister tous les objectifs pour debug
        print(f"\n=== TOUS LES OBJECTIFS ===")
        all_goals = SavingsGoal.objects.all()
        for goal in all_goals:
            print(f"ID: {goal.id}")
            print(f"  Titre: {goal.title}")
            print(f"  Utilisateur: {goal.user.email}")
            print(f"  Status: {goal.status}")
            print(f"  Créé: {goal.created_at.date()}")
            print(f"  Date activation: {goal.date_activation_caisse}")
            print(f"  Is activated: {goal.is_caisse_activated}")
            print("  ---")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    test_ma_caisse_api()
