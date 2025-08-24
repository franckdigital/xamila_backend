#!/usr/bin/env python
"""
Test des nouvelles APIs d'épargne
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

def test_savings_apis():
    """Test des APIs d'épargne avec authentification"""
    
    print("=== TEST APIS EPARGNE ===")
    
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Login pour récupérer le token
    print("\n1. Login...")
    login_data = {
        "email": "test@xamila.com",
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data['tokens']['access']
            print("OK Token récupéré")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 2. Test savings account API
            print("\n2. Test savings account...")
            response = requests.get(f"{base_url}/savings/account/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("OK Compte d'épargne récupéré")
                print(f"  - Utilisateur: {data.get('utilisateur_nom', 'N/A')}")
                print(f"  - Solde: {data.get('solde_actuel', 0)} FCFA")
                print(f"  - Objectif mensuel: {data.get('objectif_mensuel', 0)} FCFA")
                print(f"  - Progression: {data.get('progression_mensuelle', 0)}%")
            else:
                print(f"ERROR Account: {response.text[:200]}")
            
            # 3. Test transactions API
            print("\n3. Test transactions...")
            response = requests.get(f"{base_url}/savings/transactions/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', [])
                print(f"OK {len(transactions)} transactions récupérées")
                print(f"  - Total dépôts: {data.get('total_deposits', 0):,} FCFA")
                for i, tx in enumerate(transactions[:3], 1):
                    print(f"  Transaction {i}: {tx.get('amount', 0):,} FCFA ({tx.get('type', 'N/A')})")
            else:
                print(f"ERROR Transactions: {response.text[:200]}")
            
            # 4. Test stats API
            print("\n4. Test statistiques...")
            response = requests.get(f"{base_url}/savings/stats/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("OK Statistiques récupérées")
                print(f"  - Solde actuel: {data.get('solde_actuel', 0)} FCFA")
                print(f"  - Total dépôts: {data.get('total_depots', 0)} FCFA")
                print(f"  - Nombre transactions: {data.get('nombre_transactions', 0)}")
            else:
                print(f"ERROR Stats: {response.text[:200]}")
                
        else:
            print(f"ERROR Login: {response.text[:200]}")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
    
    print("\n=== RESUME ===")
    print("Test APIs épargne terminé!")

if __name__ == "__main__":
    test_savings_apis()
