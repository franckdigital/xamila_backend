#!/usr/bin/env python3
"""
Test direct de connexion sans passer par l'API
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def test_direct_login():
    print("=== TEST CONNEXION DIRECTE ===")
    
    # Vérifier si l'utilisateur existe
    try:
        user = User.objects.get(email="test@xamila.com")
        print(f"OK Utilisateur trouve: {user.email}")
        print(f"  - Actif: {user.is_active}")
        print(f"  - Verifie: {user.is_verified}")
        print(f"  - Role: {user.role}")
        
        # Test du mot de passe
        if user.check_password("test123"):
            print("OK Mot de passe correct")
            
            # Générer les tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            print(f"OK Token genere: {access_token[:50]}...")
            return access_token
        else:
            print("ERROR Mot de passe incorrect")
            return None
            
    except User.DoesNotExist:
        print("ERROR Utilisateur non trouve")
        return None

def test_api_with_token(token):
    print("\n=== TEST API AVEC TOKEN ===")
    
    import requests
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/dashboard/customer/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("OK API accessible avec token")
            data = response.json()
            print(f"Data keys: {list(data.keys())}")
        else:
            print(f"ERROR Erreur API: {response.text}")
            
    except Exception as e:
        print(f"ERROR Erreur requete: {e}")

if __name__ == "__main__":
    token = test_direct_login()
    if token:
        test_api_with_token(token)
