#!/usr/bin/env python3
"""
Test de création de cohortes avec les vrais credentials admin
"""

import requests
import json

API_BASE = "https://api.xamila.finance/api"
ADMIN_EMAIL = "franckalain.digital1@gmail.com"
ADMIN_PASSWORD = "XamilaAdmin2025!"

def get_admin_token():
    """Obtenir le token admin"""
    print("=== Connexion admin ===")
    
    login_url = f"{API_BASE}/auth/login/"
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'tokens' in data and 'access' in data['tokens']:
                print("Token obtenu avec succès")
                return data['tokens']['access']
            elif 'access' in data:
                return data['access']
        
        print(f"Erreur: {response.text}")
        return None
        
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return None

def test_cohortes_endpoints(token):
    """Test des endpoints cohortes"""
    print("\n=== Test des endpoints cohortes ===")
    
    if not token:
        print("Pas de token disponible")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test GET cohortes
    print("\n1. Test GET /admin/cohortes/")
    try:
        response = requests.get(f"{API_BASE}/admin/cohortes/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Nombre de cohortes: {data.get('count', 0)}")
        
    except Exception as e:
        print(f"Erreur GET: {e}")
    
    # Test POST création cohorte
    print("\n2. Test POST création cohorte")
    create_data = {
        "mois": 12,
        "annee": 2024,
        "email_utilisateur": "demo@xamila.finance"
    }
    
    try:
        response = requests.post(f"{API_BASE}/admin/cohortes/", headers=headers, json=create_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Erreur POST: {e}")

def test_frontend_auth():
    """Test avec les mêmes credentials que le frontend"""
    print("\n=== Test authentification frontend ===")
    
    # Simuler la même requête que le frontend
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Récupérer le token depuis localStorage (simulation)
    token = get_admin_token()
    
    if token:
        print(f"Token pour frontend: {token[:50]}...")
        
        # Test avec ce token
        auth_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{API_BASE}/admin/cohortes/", headers=auth_headers)
            print(f"Frontend test - Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ L'API fonctionne avec les credentials admin")
            else:
                print(f"✗ Erreur: {response.text}")
                
        except Exception as e:
            print(f"Erreur frontend test: {e}")

def main():
    print("Test API Cohortes avec credentials admin")
    print("=" * 50)
    
    # Obtenir le token
    token = get_admin_token()
    
    if token:
        # Tester les endpoints
        test_cohortes_endpoints(token)
        
        # Test simulation frontend
        test_frontend_auth()
    else:
        print("Impossible d'obtenir le token admin")

if __name__ == "__main__":
    main()
