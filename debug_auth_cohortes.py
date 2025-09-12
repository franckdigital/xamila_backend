#!/usr/bin/env python3
"""
Debug de l'authentification pour l'API des cohortes
"""

import requests
import json

API_BASE = "https://api.xamila.finance/api"

def test_endpoints():
    """Test des différents endpoints d'authentification"""
    print("=== Test des endpoints d'authentification ===")
    
    # Test différents endpoints de login
    login_endpoints = [
        "/auth/login/",
        "/auth/login_user/",
        "/customer/login/",
        "/admin/login/"
    ]
    
    test_user = {
        "email": "franckalain.digital1@gmail.com", 
        "password": "XamilaAdmin2025!"
    }
    
    for endpoint in login_endpoints:
        url = f"{API_BASE}{endpoint}"
        print(f"\nTest: {url}")
        
        try:
            response = requests.post(url, json=test_user)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("Endpoint fonctionnel")
                return response.json(), endpoint
                
        except Exception as e:
            print(f"Erreur: {e}")
    
    return None, None

def test_with_token(token_data, endpoint):
    """Test de l'API cohortes avec token"""
    print(f"\n=== Test API Cohortes avec token de {endpoint} ===")
    
    # Extraire le token
    token = None
    if isinstance(token_data, dict):
        if 'tokens' in token_data and 'access' in token_data['tokens']:
            token = token_data['tokens']['access']
        elif 'access' in token_data:
            token = token_data['access']
        elif 'token' in token_data:
            token = token_data['token']
    
    if not token:
        print("Pas de token trouvé dans la réponse")
        return
    
    print(f"Token: {token[:50]}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test GET cohortes
    cohortes_url = f"{API_BASE}/admin/cohortes/"
    
    try:
        print(f"\nGET {cohortes_url}")
        response = requests.get(cohortes_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Erreur: {e}")

def main():
    print("Debug authentification API Cohortes")
    print("=" * 50)
    
    # Test des endpoints
    token_data, endpoint = test_endpoints()
    
    if token_data:
        test_with_token(token_data, endpoint)
    else:
        print("\nAucun endpoint d'authentification fonctionnel trouvé")

if __name__ == "__main__":
    main()
