#!/usr/bin/env python
"""
Script pour créer des cohortes de test
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User, Cohorte

def create_test_cohortes():
    """
    Crée des cohortes de test pour les utilisateurs existants
    """
    print("=== CRÉATION DE COHORTES DE TEST ===")
    
    # Récupérer les utilisateurs de test
    users = User.objects.filter(
        email__in=['franckalain.ai@gmail.com', 'tchriffo_steph@yahoo.fr', 'm.tchriffo@outlook.com']
    )
    
    print(f"Utilisateurs trouvés: {users.count()}")
    
    if not users.exists():
        print("Aucun utilisateur de test trouvé.")
        return
    
    for user in users:
        print(f"\nCréation cohorte pour {user.email}:")
        
        # Vérifier si une cohorte existe déjà
        cohorte_existante = Cohorte.objects.filter(
            user=user,
            mois=8,
            annee=2025
        ).first()
        
        if cohorte_existante:
            print(f"  Cohorte existante: {cohorte_existante.code}")
            continue
        
        # Créer une nouvelle cohorte
        cohorte = Cohorte.objects.create(
            user=user,
            mois=8,
            annee=2025,
            email_utilisateur=user.email
        )
        
        print(f"  Cohorte créée: {cohorte.code}")
        print(f"  Nom: {cohorte.nom}")
        print(f"  Période: Août 2025")
    
    print(f"\n=== RÉSUMÉ DES COHORTES ===")
    
    # Lister toutes les cohortes
    cohortes = Cohorte.objects.all().order_by('-created_at')
    
    for cohorte in cohortes:
        mois_nom = dict(Cohorte.MOIS_CHOICES)[cohorte.mois]
        print(f"Code: {cohorte.code}")
        print(f"  Utilisateur: {cohorte.email_utilisateur}")
        print(f"  Période: {mois_nom} {cohorte.annee}")
        print(f"  Actif: {cohorte.actif}")
        print("  ---")

if __name__ == '__main__':
    create_test_cohortes()
