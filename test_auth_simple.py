#!/usr/bin/env python3
"""
Script de test simple pour l'authentification XAMILA
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"

def test_login():
    """Test de connexion avec le super admin"""
    print("=== TEST CONNEXION SUPER ADMIN ===")
    
    login_data = {
        "email": "test@xamila.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get('tokens', {}).get('access')
            print(f"OK Connexion reussie!")
            print(f"Access Token: {access_token[:50]}..." if access_token else "No token")
            return access_token
        else:
            print(f"ERROR Echec connexion: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR Erreur connexion: {e}")
        return None

def test_dashboard_api(access_token):
    """Test des endpoints dashboard avec token"""
    print("\n=== TEST DASHBOARD API ===")
    
    if not access_token:
        print("ERROR Token manquant")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/dashboard/customer/',
        '/dashboard/savings/challenges/',
        '/dashboard/savings/deposits/'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTest: {endpoint}")
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"OK {endpoint} - OK")
                print(f"Data keys: {list(result.keys())}")
            else:
                print(f"ERROR {endpoint} - Error: {response.text}")
                
        except Exception as e:
            print(f"ERROR Erreur {endpoint}: {e}")
    
    return True

def main():
    print("DEMARRAGE DES TESTS XAMILA BACKEND")
    
    # Test 1: Connexion
    access_token = test_login()
    
    # Test 2: Dashboard APIs
    if access_token:
        test_dashboard_api(access_token)
    
    print("\nTESTS TERMINES")

if __name__ == "__main__":
    main()
