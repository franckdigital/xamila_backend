#!/usr/bin/env python
"""
Script pour forcer la mise à jour des dates d'activation Ma Caisse
À exécuter sur le serveur de production
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal

def force_update_caisse_dates():
    """
    Force la mise à jour de toutes les dates d'activation
    """
    print("=== MISE À JOUR FORCÉE DES DATES D'ACTIVATION ===")
    
    # Récupérer tous les objectifs
    objectifs = SavingsGoal.objects.all()
    
    print(f"Total objectifs trouvés: {objectifs.count()}")
    
    updated_count = 0
    today = date.today()
    
    for objectif in objectifs:
        # Recalculer la date d'activation basée sur la date de création
        creation_date = objectif.created_at.date()
        new_activation_date = creation_date + timedelta(days=21)
        
        # Mettre à jour même si une date existe déjà
        old_date = objectif.date_activation_caisse
        objectif.date_activation_caisse = new_activation_date
        objectif.save()
        
        updated_count += 1
        
        is_activated = new_activation_date <= today
        days_remaining = (new_activation_date - today).days
        
        print(f"Objectif: {objectif.title}")
        print(f"  - Utilisateur: {objectif.user.email}")
        print(f"  - Créé: {creation_date}")
        print(f"  - Ancienne activation: {old_date}")
        print(f"  - Nouvelle activation: {new_activation_date}")
        print(f"  - Activé: {is_activated}")
        print(f"  - Jours restants: {days_remaining}")
        print("  ---")
    
    print(f"\nMise à jour terminée. {updated_count} objectifs mis à jour.")
    
    # Vérifier le résultat
    print(f"\n=== VÉRIFICATION ===")
    for objectif in SavingsGoal.objects.all():
        print(f"{objectif.title}: activation={objectif.date_activation_caisse}, activé={objectif.is_caisse_activated}")

if __name__ == '__main__':
    force_update_caisse_dates()
