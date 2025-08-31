#!/usr/bin/env python
"""
Script pour créer des cohortes via l'API Django (sans connexion directe DB)
"""

import requests
import json

def create_cohortes_via_api():
    """
    Crée des cohortes en utilisant l'API REST
    """
    print("=== CRÉATION DE COHORTES VIA API ===")
    
    # Configuration API
    base_url = "https://api.xamila.finance/api"
    
    # Données de connexion admin (à adapter)
    admin_login = {
        "email": "admin@xamila.finance",  # À remplacer par vos identifiants admin
        "password": "admin_password"      # À remplacer par le mot de passe admin
    }
    
    # 1. Se connecter en tant qu'admin
    print("1. Connexion admin...")
    login_response = requests.post(f"{base_url}/auth/login/", json=admin_login)
    
    if login_response.status_code != 200:
        print(f"Erreur connexion admin: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✓ Connexion admin réussie")
    
    # 2. Créer des cohortes pour les utilisateurs de test
    users_test = [
        'franckalain.ai@gmail.com',
        'tchriffo_steph@yahoo.fr',
        'm.tchriffo@outlook.com'
    ]
    
    for email in users_test:
        print(f"\n2. Création cohorte pour {email}...")
        
        cohorte_data = {
            "mois": 8,
            "annee": 2025,
            "email_utilisateur": email
        }
        
        response = requests.post(
            f"{base_url}/cohortes/creer/",
            json=cohorte_data,
            headers=headers
        )
        
        if response.status_code == 201:
            cohorte = response.json().get('cohorte', {})
            print(f"✓ Cohorte créée: {cohorte.get('code')}")
        elif response.status_code == 409:
            print("⚠ Cohorte existe déjà")
        else:
            print(f"✗ Erreur: {response.status_code}")
            print(response.text)
    
    # 3. Lister toutes les cohortes (si endpoint disponible)
    print(f"\n3. Liste des cohortes...")
    
    # Note: Cet endpoint n'existe pas encore, il faudrait l'ajouter
    # list_response = requests.get(f"{base_url}/cohortes/admin/toutes/", headers=headers)
    
    print("✓ Cohortes créées avec succès")
    print("\nPour vérifier, connectez-vous avec un utilisateur de test et allez dans le profil.")

if __name__ == '__main__':
    print("ATTENTION: Modifiez les identifiants admin dans le script avant de l'exécuter")
    print("Puis exécutez: python create_cohorte_via_api.py")
    # create_cohortes_via_api()  # Décommentez après avoir mis les bons identifiants
