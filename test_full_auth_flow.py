#!/usr/bin/env python
"""
Test complet du flux d'authentification avec les APIs du dashboard
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

def test_full_auth_flow():
    """Test complet: login + APIs dashboard avec authentification"""
    
    print("=== TEST FLUX AUTHENTIFICATION COMPLET ===")
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test login API
    print("\n1. Test login API...")
    login_data = {
        "email": "test@xamila.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'tokens' in data and 'access' in data['tokens']:
                access_token = data['tokens']['access']
                print("OK Login réussi, token récupéré")
                
                # Headers pour les requêtes authentifiées
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # 2. Test dashboard metrics avec auth
                print("\n2. Test dashboard metrics avec authentification...")
                response = requests.get(f"{base_url}/api/dashboard/customer/", headers=headers)
                print(f"Dashboard Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("OK Dashboard metrics récupérées")
                    print(f"  - Utilisateur: {data.get('user_name', 'N/A')}")
                    print(f"  - Total épargne: {data.get('total_savings', 0):,} FCFA")
                    print(f"  - Solde comptes: {data.get('total_balance', 0):,} FCFA")
                else:
                    print(f"ERROR Dashboard: {response.text[:200]}")
                
                # 3. Test challenges avec auth
                print("\n3. Test challenges avec authentification...")
                response = requests.get(f"{base_url}/api/dashboard/savings/challenges/", headers=headers)
                print(f"Challenges Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    challenges = data.get('results', [])
                    print(f"OK {len(challenges)} challenges récupérés")
                    for i, challenge in enumerate(challenges[:2], 1):
                        print(f"  Challenge {i}: {challenge.get('title', 'N/A')}")
                        print(f"    - Progrès: {challenge.get('progress', 0)}%")
                else:
                    print(f"ERROR Challenges: {response.text[:200]}")
                
                # 4. Test deposits avec auth
                print("\n4. Test deposits avec authentification...")
                response = requests.get(f"{base_url}/api/dashboard/savings/deposits/", headers=headers)
                print(f"Deposits Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    deposits = data.get('results', [])
                    print(f"OK {len(deposits)} dépôts récupérés")
                    for i, deposit in enumerate(deposits[:3], 1):
                        print(f"  Dépôt {i}: {deposit.get('amount', 0):,} FCFA")
                else:
                    print(f"ERROR Deposits: {response.text[:200]}")
                
            else:
                print(f"ERROR Login: Format de réponse invalide - {data}")
        else:
            print(f"ERROR Login: {response.text[:200]}")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n=== RESUME ===")
    print("Test flux authentification complet terminé!")

if __name__ == "__main__":
    test_full_auth_flow()
