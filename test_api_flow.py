#!/usr/bin/env python
"""
Test complet du flux API avec authentification via l'endpoint login
"""

import requests
import json

def test_complete_api_flow():
    """Tester le flux complet des APIs avec authentification"""
    
    print("=== TEST FLUX API COMPLET ===")
    
    # 1. Test de connexion via API
    print("\n1. Test connexion via API login...")
    login_data = {
        "email": "test@xamila.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OK Connexion reussie")
            print(f"Response keys: {list(data.keys())}")
            
            if 'tokens' in data and 'access' in data['tokens']:
                access_token = data['tokens']['access']
                print(f"Token obtenu: {access_token[:50]}...")
            else:
                print(f"ERROR Format de reponse invalide: {data}")
                return
        else:
            print(f"ERROR Echec connexion: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR Erreur requete: {str(e)}")
        return
    except Exception as e:
        print(f"ERROR Erreur generale: {str(e)}")
        return
    
    # Headers avec token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test API dashboard metrics
    print("\n2. Test API dashboard metrics...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/customer/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            metrics = response.json()
            print(f"OK Dashboard metrics recuperees")
            print(f"  - Utilisateur: {metrics.get('user_name')}")
            print(f"  - Total epargne: {metrics.get('total_savings', 0):,.0f} FCFA")
            print(f"  - Solde comptes: {metrics.get('account_balance', 0):,.0f} FCFA")
            print(f"  - Defis completes: {metrics.get('challenges_completed', 0)}")
        else:
            print(f"ERROR Dashboard metrics: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR Erreur dashboard: {str(e)}")
    
    # 3. Test API challenges list
    print("\n3. Test API challenges list...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/savings/challenges/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            challenges_data = response.json()
            challenges = challenges_data.get('results', [])
            print(f"OK {len(challenges)} challenges recuperes")
            
            for i, challenge in enumerate(challenges[:2], 1):
                print(f"  Challenge {i}: {challenge.get('title')}")
        else:
            print(f"ERROR Challenges list: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR Erreur challenges: {str(e)}")
    
    # 4. Test API deposits list
    print("\n4. Test API deposits list...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/savings/deposits/?limit=3",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            deposits_data = response.json()
            deposits = deposits_data.get('results', [])
            total_count = deposits_data.get('total_count', 0)
            print(f"OK {len(deposits)} depots recents (total: {total_count})")
            
            for i, deposit in enumerate(deposits, 1):
                print(f"  Depot {i}: {deposit.get('amount', 0):,.0f} FCFA")
        else:
            print(f"ERROR Deposits list: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR Erreur deposits: {str(e)}")
    
    print("\n=== RESUME ===")
    print("Test du flux API complet termine!")

if __name__ == "__main__":
    test_complete_api_flow()
