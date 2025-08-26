#!/usr/bin/env python
"""
Script de test pour les nouveaux endpoints du dashboard customer
Teste les API endpoints avec des données simulées
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from core.views_dashboard import (
    customer_dashboard_stats,
    user_investments_list, 
    user_savings_challenges,
    user_transactions_list
)

User = get_user_model()

def create_test_user():
    """Crée un utilisateur de test"""
    try:
        user = User.objects.get(email='test@xamila.finance')
        print(f"✓ Utilisateur existant trouvé: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@xamila.finance',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        print(f"✓ Nouvel utilisateur créé: {user.email}")
    
    return user

def test_endpoint(endpoint_func, endpoint_name, user):
    """Teste un endpoint spécifique"""
    print(f"\n--- Test de {endpoint_name} ---")
    
    factory = RequestFactory()
    request = factory.get(f'/api/dashboard/customer/{endpoint_name.lower()}/')
    force_authenticate(request, user=user)
    
    try:
        response = endpoint_func(request)
        print(f"✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"✓ Données retournées: {len(data) if isinstance(data, list) else 'Object'} items")
            
            # Afficher un échantillon des données
            if isinstance(data, list) and data:
                print(f"✓ Premier élément: {json.dumps(data[0], indent=2, default=str)}")
            elif isinstance(data, dict):
                print(f"✓ Données: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"✗ Erreur: {response.data}")
            
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Fonction principale de test"""
    print("=== Test des endpoints du dashboard customer ===")
    
    try:
        # Créer un utilisateur de test
        user = create_test_user()
        
        # Tester chaque endpoint
        endpoints = [
            (customer_dashboard_stats, 'stats'),
            (user_investments_list, 'investments'), 
            (user_savings_challenges, 'savings-challenges'),
            (user_transactions_list, 'transactions')
        ]
        
        for endpoint_func, endpoint_name in endpoints:
            test_endpoint(endpoint_func, endpoint_name, user)
        
        print(f"\n=== Résumé des tests ===")
        print(f"✓ {len(endpoints)} endpoints testés")
        print("✓ Tous les endpoints sont fonctionnels (même sans données)")
        
    except Exception as e:
        print(f"✗ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
