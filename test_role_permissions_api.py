#!/usr/bin/env python
"""
Script pour tester spécifiquement l'API /admin/permissions/roles/
"""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from core.models_permissions import RolePermission

User = get_user_model()

def test_role_permissions_endpoint():
    """
    Teste spécifiquement l'endpoint qui alimente les switches
    """
    admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    print("🔍 TEST ENDPOINT /admin/permissions/roles/")
    print("=" * 60)
    
    try:
        # 1. Vérifier les données en base
        print("📋 Données en base de données:")
        role_permissions = RolePermission.objects.all()
        print(f"   Total RolePermissions: {role_permissions.count()}")
        
        for rp in role_permissions:
            print(f"   - {rp.role} | {rp.permission.code} | {rp.is_granted}")
        
        # 2. Générer token admin
        admin = User.objects.get(id=admin_id)
        refresh = RefreshToken.for_user(admin)
        access_token = str(refresh.access_token)
        
        # 3. Tester l'API
        api_url = "https://api.xamila.finance/api/admin/permissions/roles/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"\n📡 Appel API: {api_url}")
        response = requests.get(api_url, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse API:")
            print(json.dumps(data, indent=2))
            
            # Analyser la structure
            if isinstance(data, list):
                print(f"\n📊 Analyse de la réponse:")
                print(f"   Type: Liste avec {len(data)} éléments")
                
                if len(data) > 0:
                    first_item = data[0]
                    print(f"   Structure du premier élément:")
                    for key, value in first_item.items():
                        print(f"     {key}: {value}")
                        
                    # Vérifier si dashboard.view pour CUSTOMER existe
                    customer_dashboard = [
                        item for item in data 
                        if item.get('role') == 'CUSTOMER' and 
                           item.get('permission_code') == 'dashboard.view'
                    ]
                    
                    if customer_dashboard:
                        print(f"\n🎯 Permission dashboard.view pour CUSTOMER:")
                        print(json.dumps(customer_dashboard[0], indent=2))
                    else:
                        print(f"\n❌ Permission dashboard.view pour CUSTOMER non trouvée")
                        
                else:
                    print(f"   ⚠️  Liste vide")
            else:
                print(f"   ⚠️  Réponse n'est pas une liste: {type(data)}")
                
        else:
            print(f"❌ Erreur API:")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_role_permissions_endpoint()
