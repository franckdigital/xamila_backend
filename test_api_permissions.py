#!/usr/bin/env python
"""
Script pour tester directement l'API permissions
"""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_permissions_api():
    """
    Teste l'API permissions directement
    """
    admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    print("🧪 TEST API PERMISSIONS")
    print("=" * 50)
    
    try:
        # 1. Récupérer l'admin
        admin = User.objects.get(id=admin_id)
        print(f"✅ Admin: {admin.email}")
        
        # 2. Générer un token frais
        refresh = RefreshToken.for_user(admin)
        access_token = str(refresh.access_token)
        print(f"🔑 Token généré")
        
        # 3. Tester l'API /admin/permissions/roles/
        api_url = "https://api.xamila.finance/api/admin/permissions/roles/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"\n📡 Test API: {api_url}")
        response = requests.get(api_url, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse JSON:")
            print(json.dumps(data, indent=2))
            
            if isinstance(data, list) and len(data) > 0:
                print(f"\n📊 Analyse:")
                print(f"   Nombre d'éléments: {len(data)}")
                for item in data[:3]:  # Afficher les 3 premiers
                    print(f"   - Role: {item.get('role')}")
                    print(f"     Permission: {item.get('permission_code')}")
                    print(f"     Accordée: {item.get('is_granted')}")
            else:
                print(f"⚠️  Liste vide ou format incorrect")
                
        else:
            print(f"❌ Erreur API:")
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
        # 4. Tester l'API /admin/permissions/update/
        print(f"\n📡 Test API Update:")
        update_url = "https://api.xamila.finance/api/admin/permissions/update/"
        update_data = {
            "role": "CUSTOMER",
            "permission_code": "dashboard.view",
            "is_granted": True
        }
        
        update_response = requests.post(update_url, headers=headers, json=update_data)
        print(f"Update Status: {update_response.status_code}")
        print(f"Update Response: {update_response.text}")
        
    except User.DoesNotExist:
        print(f"❌ Admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_permissions_api()
