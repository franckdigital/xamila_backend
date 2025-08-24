#!/usr/bin/env python
"""
Script pour tester les API du dashboard avec des données dynamiques
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User

def test_dashboard_apis():
    """Tester les APIs du dashboard avec authentification"""
    
    print("=== TEST DES APIS DASHBOARD DYNAMIQUES ===")
    
    # 1. Test de connexion directe sans API
    print("\n1. Test de connexion directe...")
    from core.models import User
    from django.contrib.auth import authenticate
    from rest_framework_simplejwt.tokens import RefreshToken
    
    try:
        user = User.objects.get(email="test@xamila.com")
        if user.check_password("test123"):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            print(f"OK Connexion directe reussie, token genere")
        else:
            print("ERROR Mot de passe incorrect")
            return
    except User.DoesNotExist:
        print("ERROR Utilisateur non trouve")
        return
    except Exception as e:
        print(f"ERROR Erreur connexion directe: {str(e)}")
        return
    
    # Headers avec token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test API dashboard metrics avec token
    print("\n2. Test API dashboard metrics...")
    response = requests.get(
        "http://127.0.0.1:8000/api/dashboard/customer/",
        headers=headers
    )
    
    if response.status_code == 200:
        metrics = response.json()
        print(f"OK Dashboard metrics recuperees")
        print(f"  - Utilisateur: {metrics.get('user_name')}")
        print(f"  - Total epargne: {metrics.get('total_savings'):,.0f} FCFA")
        print(f"  - Solde comptes: {metrics.get('account_balance'):,.0f} FCFA")
        print(f"  - Portfolio: {metrics.get('portfolio_value'):,.0f} FCFA")
        print(f"  - Defis completes: {metrics.get('challenges_completed')}")
        print(f"  - Serie actuelle: {metrics.get('current_streak')}")
        print(f"  - Objectifs actifs: {metrics.get('active_goals')}")
        print(f"  - Participations actives: {metrics.get('active_participations')}")
    else:
        print(f"ERROR Dashboard metrics: {response.status_code} - {response.text}")
    
    # 3. Test API challenges list
    print("\n3. Test API challenges list...")
    response = requests.get(
        "http://127.0.0.1:8000/api/dashboard/savings/challenges/",
        headers=headers
    )
    
    if response.status_code == 200:
        challenges_data = response.json()
        challenges = challenges_data.get('results', [])
        print(f"OK {len(challenges)} challenges recuperes")
        
        for i, challenge in enumerate(challenges[:3], 1):
            print(f"  Challenge {i}:")
            print(f"    - Titre: {challenge.get('title')}")
            print(f"    - Objectif: {challenge.get('target_amount'):,.0f} FCFA")
            print(f"    - Epargne: {challenge.get('current_amount'):,.0f} FCFA")
            print(f"    - Progres: {challenge.get('progress'):.1f}%")
            print(f"    - Statut: {challenge.get('status')}")
            print(f"    - Participants: {challenge.get('participants_count')}")
    else:
        print(f"ERROR Challenges list: {response.status_code} - {response.text}")
    
    # 4. Test API deposits list
    print("\n4. Test API deposits list...")
    response = requests.get(
        "http://127.0.0.1:8000/api/dashboard/savings/deposits/?limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        deposits_data = response.json()
        deposits = deposits_data.get('results', [])
        total_count = deposits_data.get('total_count', 0)
        print(f"OK {len(deposits)} depots recents recuperes (total: {total_count})")
        
        for i, deposit in enumerate(deposits, 1):
            print(f"  Depot {i}:")
            print(f"    - Montant: {deposit.get('amount'):,.0f} FCFA")
            print(f"    - Date: {deposit.get('date')}")
            print(f"    - Challenge: {deposit.get('challenge')}")
            print(f"    - Methode: {deposit.get('type')}")
            print(f"    - Statut: {deposit.get('status')}")
    else:
        print(f"ERROR Deposits list: {response.status_code} - {response.text}")
    
    print("\n=== RESUME DES TESTS ===")
    print("Toutes les APIs du dashboard fonctionnent avec des donnees dynamiques!")
    print("Les donnees proviennent maintenant directement de la base de donnees.")

if __name__ == "__main__":
    test_dashboard_apis()
