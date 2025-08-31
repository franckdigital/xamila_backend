#!/usr/bin/env python
"""
Script pour corriger les dates d'activation None
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal

def fix_activation_dates():
    """
    Corrige les objectifs avec date_activation_caisse = None
    """
    print("=== CORRECTION DES DATES D'ACTIVATION ===")
    
    # Trouver les objectifs avec date_activation_caisse = None
    objectifs_sans_date = SavingsGoal.objects.filter(date_activation_caisse__isnull=True)
    
    print(f"Objectifs sans date d'activation: {objectifs_sans_date.count()}")
    
    for objectif in objectifs_sans_date:
        # Calculer la date d'activation basée sur created_at
        creation_date = objectif.created_at.date()
        activation_date = creation_date + timedelta(days=21)
        
        print(f"Objectif: {objectif.title}")
        print(f"  Utilisateur: {objectif.user.email}")
        print(f"  Créé: {creation_date}")
        print(f"  Nouvelle activation: {activation_date}")
        
        # Mettre à jour
        objectif.date_activation_caisse = activation_date
        objectif.save()
        
        print(f"  Activé: {objectif.is_caisse_activated}")
        print("  ---")
    
    print(f"\n=== VÉRIFICATION FINALE ===")
    
    # Vérifier tous les objectifs
    tous_objectifs = SavingsGoal.objects.all()
    
    for objectif in tous_objectifs:
        print(f"{objectif.user.email} - {objectif.title}:")
        print(f"  Activation: {objectif.date_activation_caisse}")
        print(f"  Activé: {objectif.is_caisse_activated}")

if __name__ == '__main__':
    fix_activation_dates()
