#!/usr/bin/env python
"""
Test de l'API collective-progress
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

def test_collective_progress():
    """Test de l'API collective-progress avec authentification"""
    
    print("=== TEST API COLLECTIVE PROGRESS ===")
    
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
            
            # 2. Test collective-progress
            print("\n2. Test collective-progress...")
            response = requests.get(f"{base_url}/savings/collective-progress/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("OK Progression collective récupérée")
                
                # Afficher les statistiques communautaires
                community_stats = data.get('community_stats', {})
                print(f"  - Participants totaux: {community_stats.get('total_participants', 0)}")
                print(f"  - Montant total épargné: {community_stats.get('total_saved', 0):,} FCFA")
                print(f"  - Niveau communauté: {community_stats.get('community_level', 0)}")
                print(f"  - Progression: {community_stats.get('progress_to_next', 0):.1f}%")
                
                # Afficher les top savers
                top_savers = data.get('top_savers', [])
                print(f"  - Top savers: {len(top_savers)}")
                for saver in top_savers[:5]:
                    print(f"    * {saver.get('display_name', 'N/A')}: {saver.get('amount', 0):,} FCFA (Niveau {saver.get('level', 0)})")
                
                # Afficher l'utilisateur actuel
                current_user = data.get('current_user')
                if current_user:
                    print(f"  - Utilisateur actuel: {current_user.get('display_name', 'N/A')}")
                    print(f"    * Rang: #{current_user.get('rank', 0)}")
                    print(f"    * Montant: {current_user.get('amount', 0):,} FCFA")
                    print(f"    * Niveau: {current_user.get('level', 0)}")
                else:
                    print("  - Aucun utilisateur actuel trouvé")
                
            else:
                print(f"ERROR Collective Progress: {response.text[:200]}")
                
        else:
            print(f"ERROR Login: {response.text[:200]}")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
    
    print("\n=== RESUME ===")
    print("Test API collective-progress terminé!")

if __name__ == "__main__":
    test_collective_progress()
