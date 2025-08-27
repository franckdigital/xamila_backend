#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Ajouter le répertoire du projet au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def test_api_response():
    """Tester la réponse exacte de l'API pour le dashboard admin"""
    
    print("=== TEST RÉPONSE API ===\n")
    
    # 1. Simuler la réponse de l'API /api/admin/role-permissions/
    print("1. SIMULATION RÉPONSE API:")
    
    # Récupérer toutes les permissions par rôle (comme dans la vue)
    role_permissions_data = {}
    
    # Obtenir tous les rôles uniques
    roles = RolePermission.objects.values_list('role', flat=True).distinct().order_by('role')
    
    for role in roles:
        role_permissions_data[role] = {}
        role_perms = RolePermission.objects.filter(role=role).select_related('permission')
        
        for rp in role_perms:
            role_permissions_data[role][rp.permission.code] = rp.is_granted
    
    api_response = {
        "role_permissions": role_permissions_data
    }
    
    print("Réponse API complète:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # 2. Vérifier spécifiquement BASIC
    print(f"\n2. VÉRIFICATION BASIC:")
    if 'BASIC' in api_response['role_permissions']:
        basic_data = api_response['role_permissions']['BASIC']
        print(f"   ✅ BASIC trouvé dans la réponse")
        print(f"   - Permissions BASIC: {basic_data}")
        
        if 'bilans_financiers' in basic_data:
            print(f"   ✅ bilans_financiers présent: {basic_data['bilans_financiers']}")
        else:
            print(f"   ❌ bilans_financiers ABSENT")
    else:
        print(f"   ❌ BASIC ABSENT de la réponse")
    
    # 3. Comparer avec les rôles hardcodés dans le frontend
    frontend_roles = ['CUSTOMER', 'BASIC', 'STUDENT', 'SGI_MANAGER', 'INSTRUCTOR', 'SUPPORT', 'ADMIN']
    api_roles = list(api_response['role_permissions'].keys())
    
    print(f"\n3. COMPARAISON FRONTEND/API:")
    print(f"   Frontend attend: {frontend_roles}")
    print(f"   API retourne: {api_roles}")
    
    missing_in_api = [role for role in frontend_roles if role not in api_roles]
    missing_in_frontend = [role for role in api_roles if role not in frontend_roles]
    
    if missing_in_api:
        print(f"   ❌ Manquant dans API: {missing_in_api}")
    if missing_in_frontend:
        print(f"   ⚠️ Supplémentaire dans API: {missing_in_frontend}")
    
    if not missing_in_api and not missing_in_frontend:
        print(f"   ✅ Correspondance parfaite")
    
    # 4. Vérifier les permissions attendues par le frontend
    frontend_permissions = [
        'savings_plans', 'trading_education', 'portfolio', 'my_sgi', 
        'ma_caisse', 'savings_challenge', 'bilans_financiers',
        'user_management', 'sgi_management', 'contract_management', 'client_management',
        'my_courses', 'learning', 'quizzes', 'certificates', 'progress',
        'tickets', 'reports', 'analytics',
        'admin_dashboard', 'role_management', 'security', 'notifications'
    ]
    
    print(f"\n4. VÉRIFICATION PERMISSIONS:")
    
    # Vérifier que toutes les permissions frontend existent dans l'API
    all_api_permissions = set()
    for role_perms in api_response['role_permissions'].values():
        all_api_permissions.update(role_perms.keys())
    
    missing_permissions = [perm for perm in frontend_permissions if perm not in all_api_permissions]
    extra_permissions = [perm for perm in all_api_permissions if perm not in frontend_permissions]
    
    if missing_permissions:
        print(f"   ❌ Permissions manquantes dans API: {missing_permissions}")
    if extra_permissions:
        print(f"   ⚠️ Permissions supplémentaires dans API: {extra_permissions}")
    
    # 5. Test direct de l'endpoint (si possible)
    print(f"\n5. TEST ENDPOINT DIRECT:")
    try:
        # Essayer d'appeler l'endpoint directement
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Créer un client de test
        client = Client()
        
        # Essayer de trouver un admin
        admin_user = User.objects.filter(role='ADMIN').first()
        if admin_user:
            # Simuler une connexion
            client.force_login(admin_user)
            
            # Appeler l'endpoint
            response = client.get('/api/admin/role-permissions/')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible")
                
                if 'role_permissions' in data and 'BASIC' in data['role_permissions']:
                    print(f"   ✅ BASIC présent dans la réponse endpoint")
                else:
                    print(f"   ❌ BASIC absent de la réponse endpoint")
            else:
                print(f"   ❌ Erreur endpoint: {response.content}")
        else:
            print(f"   ⚠️ Aucun utilisateur ADMIN trouvé pour le test")
            
    except Exception as e:
        print(f"   ❌ Erreur test endpoint: {e}")

if __name__ == '__main__':
    test_api_response()
