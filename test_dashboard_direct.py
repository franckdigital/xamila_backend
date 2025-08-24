#!/usr/bin/env python
"""
Test direct des APIs dashboard en contournant l'API login
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_dashboard_direct():
    """Tester les APIs dashboard directement avec token généré"""
    
    print("=== TEST DASHBOARD DIRECT ===")
    
    # 1. Générer token directement
    print("\n1. Generation token direct...")
    try:
        user = User.objects.get(email="test@xamila.com")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"OK Token genere pour {user.email}")
    except Exception as e:
        print(f"ERROR Generation token: {str(e)}")
        return
    
    # Headers avec token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test API dashboard metrics (sans authentification maintenant)
    print("\n2. Test dashboard metrics...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/customer/",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            metrics = response.json()
            print(f"OK Metrics recuperees")
            print(f"  - Utilisateur: {metrics.get('user_name')}")
            print(f"  - Total epargne: {metrics.get('total_savings', 0):,.0f} FCFA")
            print(f"  - Solde comptes: {metrics.get('account_balance', 0):,.0f} FCFA")
            print(f"  - Defis completes: {metrics.get('challenges_completed', 0)}")
            print(f"  - Objectifs actifs: {metrics.get('active_goals', 0)}")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR Dashboard: {str(e)}")
    
    # 3. Test API challenges
    print("\n3. Test challenges list...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/savings/challenges/",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            challenges = data.get('results', [])
            print(f"OK {len(challenges)} challenges recuperes")
            
            for i, challenge in enumerate(challenges[:2], 1):
                print(f"  Challenge {i}: {challenge.get('title')}")
                print(f"    - Progres: {challenge.get('progress', 0):.1f}%")
                print(f"    - Montant: {challenge.get('current_amount', 0):,.0f} FCFA")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR Challenges: {str(e)}")
    
    # 4. Test API deposits
    print("\n4. Test deposits list...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/savings/deposits/?limit=3",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            deposits = data.get('results', [])
            total = data.get('total_count', 0)
            print(f"OK {len(deposits)} depots recuperes (total: {total})")
            
            for i, deposit in enumerate(deposits, 1):
                print(f"  Depot {i}: {deposit.get('amount', 0):,.0f} FCFA")
                print(f"    - Date: {deposit.get('created_at', 'N/A')}")
                print(f"    - Statut: {deposit.get('status', 'N/A')}")
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"ERROR Deposits: {str(e)}")
    
    print("\n=== RESUME ===")
    print("Test dashboard direct termine!")

if __name__ == "__main__":
    test_dashboard_direct()
