#!/usr/bin/env python
"""
Test de l'API de dépôt d'épargne
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

def test_deposit_api():
    """Test de l'API de dépôt avec authentification"""
    
    print("=== TEST API DEPOT EPARGNE ===")
    
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Login pour récupérer le token
    print("\n1. Login...")
    login_data = {
        "email": "test@xamila.com",
        "password": "test123"
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
            
            # 2. Vérifier le solde avant dépôt
            print("\n2. Solde avant dépôt...")
            response = requests.get(f"{base_url}/savings/account/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                solde_avant = float(data.get('solde_actuel', 0))
                print(f"Solde avant: {solde_avant:,} FCFA")
            else:
                print(f"ERROR Account: {response.text[:200]}")
                return
            
            # 3. Test dépôt
            print("\n3. Test dépôt de 25,000 FCFA...")
            deposit_data = {
                "montant": 25000,
                "methode_depot": "bank",
                "banque": "ADEC"
            }
            
            response = requests.post(f"{base_url}/savings/deposit/", json=deposit_data, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("OK Dépôt créé avec succès")
                print(f"  - Message: {data.get('message', 'N/A')}")
                print(f"  - Nouveau solde: {data.get('nouveau_solde', 0)} FCFA")
                print(f"  - Référence: {data.get('reference', 'N/A')}")
                
                # Vérifier l'augmentation du solde
                nouveau_solde = float(data.get('nouveau_solde', 0))
                augmentation = nouveau_solde - solde_avant
                print(f"  - Augmentation: {augmentation:,} FCFA")
                
            else:
                print(f"ERROR Deposit: {response.text[:200]}")
            
            # 4. Vérifier le solde après dépôt
            print("\n4. Vérification solde après dépôt...")
            response = requests.get(f"{base_url}/savings/account/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                solde_apres = float(data.get('solde_actuel', 0))
                print(f"Solde après: {solde_apres:,} FCFA")
            
            # 5. Vérifier les nouvelles transactions
            print("\n5. Vérification nouvelles transactions...")
            response = requests.get(f"{base_url}/savings/transactions/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', [])
                print(f"Nombre de transactions: {len(transactions)}")
                if transactions:
                    last_tx = transactions[0]  # Plus récente en premier
                    print(f"Dernière transaction: {last_tx.get('amount', 0):,} FCFA ({last_tx.get('type', 'N/A')})")
                
        else:
            print(f"ERROR Login: {response.text[:200]}")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
    
    print("\n=== RESUME ===")
    print("Test API dépôt terminé!")

if __name__ == "__main__":
    test_deposit_api()
