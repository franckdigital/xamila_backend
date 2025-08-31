#!/usr/bin/env python
"""
Script pour tester directement les endpoints API
"""

import os
import sys
import django
import json
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.views_ma_caisse import verifier_activation_caisse, statut_objectifs_epargne
from core.views_cohorte import mes_cohortes
from core.models_savings_challenge import SavingsGoal
from core.models_cohorte import Cohorte

User = get_user_model()

def test_endpoints():
    """
    Test les endpoints API directement
    """
    print("=== TEST ENDPOINTS API ===")
    
    # Créer une factory de requêtes
    factory = RequestFactory()
    
    # Récupérer un utilisateur de test
    user = User.objects.filter(email__icontains='demo').first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("Aucun utilisateur trouvé")
        return
    
    print(f"Test avec utilisateur: {user.email}")
    
    # Test 1: API Ma Caisse
    print(f"\n=== TEST API MA CAISSE ===")
    
    request = factory.get('/api/ma-caisse/verifier-activation/')
    request.user = user
    
    try:
        response = verifier_activation_caisse(request)
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        
        # Vérifier les objectifs de cet utilisateur
        objectifs = SavingsGoal.objects.filter(user=user, status='ACTIVE')
        print(f"\nObjectifs actifs de l'utilisateur: {objectifs.count()}")
        
        for obj in objectifs:
            print(f"  - {obj.title}: activation={obj.date_activation_caisse}, activé={obj.is_caisse_activated}")
            
    except Exception as e:
        print(f"Erreur API Ma Caisse: {e}")
    
    # Test 2: API Cohortes
    print(f"\n=== TEST API COHORTES ===")
    
    request = factory.get('/api/cohortes/mes-cohortes/')
    request.user = user
    
    try:
        response = mes_cohortes(request)
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        
        # Vérifier les cohortes de cet utilisateur
        cohortes = Cohorte.objects.filter(utilisateur=user)
        print(f"\nCohortes de l'utilisateur: {cohortes.count()}")
        
        for cohorte in cohortes:
            print(f"  - {cohorte.code}: {cohorte.nom}")
            
    except Exception as e:
        print(f"Erreur API Cohortes: {e}")
    
    # Test 3: Vérifier la structure de la base de données
    print(f"\n=== VERIFICATION BASE DE DONNEES ===")
    
    # Vérifier les champs du modèle SavingsGoal
    print("Champs SavingsGoal:")
    for field in SavingsGoal._meta.fields:
        print(f"  - {field.name}: {field.__class__.__name__}")
    
    # Vérifier les champs du modèle Cohorte
    print("\nChamps Cohorte:")
    for field in Cohorte._meta.fields:
        print(f"  - {field.name}: {field.__class__.__name__}")

if __name__ == '__main__':
    test_endpoints()
