#!/usr/bin/env python
"""
Script de debug rapide pour les deux problèmes
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal
from core.models import Cohorte
from core.models import User

def quick_debug():
    print("=== DEBUG RAPIDE ===")
    
    # 1. Vérifier Ma Caisse
    print("1. MA CAISSE:")
    goals = SavingsGoal.objects.all()
    print(f"   Total objectifs: {goals.count()}")
    
    today = date.today()
    for goal in goals:
        days_since_creation = (today - goal.created_at.date()).days
        print(f"   - {goal.title}: créé il y a {days_since_creation} jours, activation={goal.date_activation_caisse}, activé={goal.is_caisse_activated}")
    
    # 2. Vérifier Cohortes
    print("\n2. COHORTES:")
    cohortes = Cohorte.objects.all()
    print(f"   Total cohortes: {cohortes.count()}")
    
    for cohorte in cohortes:
        print(f"   - {cohorte.code} pour {cohorte.utilisateur.email}")
    
    # 3. Vérifier utilisateurs
    print(f"\n3. UTILISATEURS:")
    users = User.objects.all()
    for user in users:
        user_goals = SavingsGoal.objects.filter(user=user).count()
        user_cohortes = Cohorte.objects.filter(utilisateur=user).count()
        print(f"   - {user.email}: {user_goals} objectifs, {user_cohortes} cohortes")

if __name__ == '__main__':
    quick_debug()
