#!/usr/bin/env python
"""
Script pour corriger l'activation de Ma Caisse
Met à jour les objectifs existants pour avoir la bonne date d'activation (21 jours après création)
"""

import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_savings_challenge import SavingsGoal

def fix_caisse_activation():
    """
    Met à jour tous les objectifs d'épargne existants pour avoir la bonne date d'activation
    """
    print("Correction de l'activation Ma Caisse...")
    
    # Récupérer tous les objectifs sans date d'activation
    objectifs_sans_date = SavingsGoal.objects.filter(date_activation_caisse__isnull=True)
    
    print(f"Objectifs trouvés sans date d'activation: {objectifs_sans_date.count()}")
    
    updated_count = 0
    
    for objectif in objectifs_sans_date:
        # Calculer la date d'activation basée sur la date de création + 21 jours
        creation_date = objectif.created_at.date()
        activation_date = creation_date + timedelta(days=21)
        
        # Mettre à jour l'objectif
        objectif.date_activation_caisse = activation_date
        objectif.save()
        
        updated_count += 1
        
        print(f"Objectif '{objectif.title}' - Activation: {activation_date} (Cree: {creation_date})")
    
    # Vérifier les objectifs avec activation immédiate (créés aujourd'hui)
    today = date.today()
    objectifs_immediats = SavingsGoal.objects.filter(
        created_at__date=today,
        date_activation_caisse__lte=today
    )
    
    if objectifs_immediats.exists():
        print(f"\nObjectifs avec activation immediate detectes: {objectifs_immediats.count()}")
        
        for objectif in objectifs_immediats:
            # Recalculer la date d'activation
            new_activation_date = today + timedelta(days=21)
            objectif.date_activation_caisse = new_activation_date
            objectif.save()
            
            print(f"Corrige: '{objectif.title}' - Nouvelle activation: {new_activation_date}")
    
    print(f"\nCorrection terminee. {updated_count} objectifs mis a jour.")
    
    # Afficher un résumé
    print("\nResume des objectifs:")
    all_objectifs = SavingsGoal.objects.all().order_by('created_at')
    
    for objectif in all_objectifs:
        is_activated = objectif.is_caisse_activated
        status_icon = "ACTIVE" if is_activated else "PENDING"
        days_remaining = (objectif.date_activation_caisse - today).days if objectif.date_activation_caisse and not is_activated else 0
        
        print(f"{status_icon} {objectif.title} - Activation: {objectif.date_activation_caisse} - "
              f"{'Active' if is_activated else f'Dans {days_remaining} jours'}")

if __name__ == '__main__':
    fix_caisse_activation()
