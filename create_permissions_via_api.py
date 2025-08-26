#!/usr/bin/env python
"""
Script pour créer les permissions via l'API REST au lieu de la base de données directement
"""
import requests
import json

# Configuration
API_BASE_URL = "https://api.xamila.finance"
ADMIN_EMAIL = "admin@xamila.finance"
ADMIN_PASSWORD = "Admin123!"

def get_admin_token():
    """Obtenir le token JWT admin"""
    login_url = f"{API_BASE_URL}/api/auth/admin/login/"
    
    response = requests.post(login_url, json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data['tokens']['access']
    else:
        print(f"Erreur login: {response.status_code} - {response.text}")
        return None

def create_permission_via_api(token, perm_data):
    """Créer une permission via l'API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Endpoint pour créer une permission (à créer si n'existe pas)
    url = f"{API_BASE_URL}/api/admin/permissions/create/"
    
    response = requests.post(url, headers=headers, json=perm_data)
    return response

def assign_permission_to_role_via_api(token, role, permission_code, is_granted=True):
    """Assigner une permission à un rôle via l'API existante"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{API_BASE_URL}/api/admin/permissions/update/"
    
    data = {
        "role": role,
        "permission_code": permission_code,
        "is_granted": is_granted
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response

def main():
    print("CREATION PERMISSIONS VIA API")
    print("=" * 50)
    
    # 1. Obtenir le token
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return
    
    print("Token admin obtenu ✓")
    
    # 2. Permissions à créer
    permissions_to_create = [
        {'code': 'savings.view', 'name': 'Voir Épargne', 'category': 'Épargne', 'description': 'Consulter les données d\'épargne'},
        {'code': 'savings.challenges', 'name': 'Challenges Épargne', 'category': 'Épargne', 'description': 'Gérer les défis d\'épargne'},
        {'code': 'education.view', 'name': 'Voir Formation', 'category': 'Formation', 'description': 'Accéder aux contenus éducatifs'},
        {'code': 'investments.view', 'name': 'Voir Investissements', 'category': 'Investissement', 'description': 'Consulter les investissements'},
        {'code': 'support.create', 'name': 'Créer Tickets Support', 'category': 'Support', 'description': 'Créer des tickets de support'}
    ]
    
    # 3. Assigner directement les permissions aux rôles (l'API créera les permissions si nécessaire)
    role_permissions = {
        'CUSTOMER': ['dashboard.view', 'savings.view', 'savings.challenges', 'education.view', 'investments.view', 'support.create']
    }
    
    print("\nAssignation permissions CUSTOMER:")
    for role, permissions in role_permissions.items():
        print(f"\nRôle: {role}")
        for perm_code in permissions:
            response = assign_permission_to_role_via_api(token, role, perm_code, True)
            if response.status_code == 200:
                print(f"  ✓ {perm_code}: Assignée")
            else:
                print(f"  ✗ {perm_code}: Erreur {response.status_code}")
                print(f"    Response: {response.text}")
    
    print(f"\n" + "=" * 50)
    print("PERMISSIONS CUSTOMER CONFIGURÉES")
    print("Testez maintenant les switches dans l'interface admin")
    print("=" * 50)

if __name__ == '__main__':
    main()
