#!/usr/bin/env python
"""
Script pour lister toutes les cohortes créées
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import Cohorte

def list_all_cohortes():
    """
    Liste toutes les cohortes dans la base de données
    """
    print("=== LISTE DE TOUTES LES COHORTES ===")
    
    cohortes = Cohorte.objects.all().order_by('-created_at')
    
    print(f"Total cohortes trouvées: {cohortes.count()}")
    
    if not cohortes.exists():
        print("Aucune cohorte trouvée dans la base de données.")
        return
    
    print("\nDétails des cohortes:")
    print("-" * 80)
    
    for cohorte in cohortes:
        mois_nom = dict(Cohorte.MOIS_CHOICES)[cohorte.mois]
        
        print(f"ID: {cohorte.id}")
        print(f"Code: {cohorte.code}")
        print(f"Nom: {cohorte.nom}")
        print(f"Période: {mois_nom} {cohorte.annee}")
        print(f"Utilisateur: {cohorte.user.email if cohorte.user else 'N/A'}")
        print(f"Email utilisateur: {cohorte.email_utilisateur}")
        print(f"User ID: {cohorte.user_id}")
        print(f"Actif: {cohorte.actif}")
        print(f"Créé le: {cohorte.created_at}")
        print("-" * 80)

if __name__ == '__main__':
    list_all_cohortes()
