#!/usr/bin/env python
"""
Script pour créer des objectifs d'épargne de test
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

def create_test_savings_goals():
    """
    Crée des objectifs d'épargne de test pour différents utilisateurs
    """
    print("=== CRÉATION D'OBJECTIFS D'ÉPARGNE DE TEST ===")
    
    # Trouver des utilisateurs existants
    users = User.objects.all()[:3]  # Prendre les 3 premiers utilisateurs
    
    if not users:
        print("Aucun utilisateur trouvé. Créer d'abord des utilisateurs.")
        return
    
    print(f"Utilisateurs trouvés: {users.count()}")
    
    for i, user in enumerate(users):
        print(f"\nCréation d'objectifs pour {user.email}:")
        
        # Objectif 1: Créé aujourd'hui (pas encore activé)
        goal1 = SavingsGoal.objects.create(
            user=user,
            title=f"Objectif Récent - {user.first_name}",
            description="Objectif créé aujourd'hui",
            target_amount=1000.00,
            current_amount=0.00,
            target_date=date.today() + timedelta(days=90)
        )
        print(f"  - {goal1.title}: activation le {goal1.date_activation_caisse}")
        
        # Objectif 2: Créé il y a 25 jours (déjà activé)
        old_date = date.today() - timedelta(days=25)
        goal2 = SavingsGoal.objects.create(
            user=user,
            title=f"Objectif Ancien - {user.first_name}",
            description="Objectif créé il y a 25 jours",
            target_amount=2000.00,
            current_amount=500.00,
            target_date=date.today() + timedelta(days=65)
        )
        # Forcer la date de création
        goal2.created_at = old_date
        goal2.date_activation_caisse = old_date + timedelta(days=21)
        goal2.save()
        print(f"  - {goal2.title}: activation le {goal2.date_activation_caisse} (activé: {goal2.is_caisse_activated})")
    
    print(f"\n=== RÉSUMÉ ===")
    all_goals = SavingsGoal.objects.all()
    print(f"Total objectifs créés: {all_goals.count()}")
    
    for goal in all_goals:
        print(f"{goal.user.email} - {goal.title}:")
        print(f"  Activation: {goal.date_activation_caisse}")
        print(f"  Activé: {goal.is_caisse_activated}")

if __name__ == '__main__':
    create_test_savings_goals()
