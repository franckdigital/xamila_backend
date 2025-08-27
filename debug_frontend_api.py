#!/usr/bin/env python
import os
import sys
import django
import json

# Ajouter le répertoire du projet au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def debug_frontend_api():
    """Debug spécifique pour comprendre pourquoi BASIC n'apparaît pas dans le frontend"""
    
    print("=== DEBUG FRONTEND/API MISMATCH ===\n")
    
    # 1. Vérifier la structure exacte attendue par le frontend
    print("1. STRUCTURE ATTENDUE PAR LE FRONTEND:")
    print("   Le frontend RolePermissionManagement.js attend:")
    print("   - Une réponse avec clé 'role_permissions'")
    print("   - Chaque rôle comme clé avec ses permissions")
    print("   - Format: { role_permissions: { BASIC: { bilans_financiers: true } } }")
    
    # 2. Générer la réponse exacte de l'API
    print("\n2. RÉPONSE ACTUELLE DE L'API:")
    
    role_permissions_data = {}
    roles = RolePermission.objects.values_list('role', flat=True).distinct().order_by('role')
    
    for role in roles:
        role_permissions_data[role] = {}
        role_perms = RolePermission.objects.filter(role=role).select_related('permission')
        
        for rp in role_perms:
            role_permissions_data[role][rp.permission.code] = rp.is_granted
    
    api_response = {
        "role_permissions": role_permissions_data
    }
    
    print(f"   Rôles dans la réponse: {list(role_permissions_data.keys())}")
    
    # 3. Vérifier BASIC spécifiquement
    print(f"\n3. ANALYSE DU RÔLE BASIC:")
    
    if 'BASIC' in role_permissions_data:
        basic_perms = role_permissions_data['BASIC']
        print(f"   ✅ BASIC présent avec {len(basic_perms)} permissions")
        print(f"   - Permissions: {list(basic_perms.keys())}")
        
        for perm_code, is_granted in basic_perms.items():
            print(f"     * {perm_code}: {'✅ Accordée' if is_granted else '❌ Refusée'}")
    else:
        print(f"   ❌ BASIC ABSENT de la réponse")
        print(f"   Rôles disponibles: {list(role_permissions_data.keys())}")
    
    # 4. Vérifier les permissions hardcodées dans le frontend
    print(f"\n4. PERMISSIONS HARDCODÉES FRONTEND:")
    
    frontend_permissions = [
        { 'code': 'savings_plans', 'name': 'Plans Épargne', 'category': 'Services Financiers' },
        { 'code': 'trading_education', 'name': 'Formation Bourse', 'category': 'Services Financiers' },
        { 'code': 'portfolio', 'name': 'Mon Portefeuille', 'category': 'Services Financiers' },
        { 'code': 'my_sgi', 'name': 'Mes SGI', 'category': 'Services Financiers' },
        { 'code': 'ma_caisse', 'name': 'Ma Caisse', 'category': 'Services Financiers' },
        { 'code': 'savings_challenge', 'name': 'Défis Épargne', 'category': 'Services Financiers' },
        { 'code': 'bilans_financiers', 'name': 'Bilans Financiers', 'category': 'Services Financiers' },
    ]
    
    print(f"   Permissions Services Financiers attendues par le frontend:")
    for perm in frontend_permissions:
        exists_in_db = Permission.objects.filter(code=perm['code']).exists()
        status = "✅ Existe" if exists_in_db else "❌ Manque"
        print(f"     - {perm['code']} ({perm['name']}): {status}")
    
    # 5. Problème potentiel: ordre des rôles
    print(f"\n5. ORDRE DES RÔLES:")
    
    frontend_role_order = ['CUSTOMER', 'BASIC', 'STUDENT', 'SGI_MANAGER', 'INSTRUCTOR', 'SUPPORT', 'ADMIN']
    api_role_order = list(role_permissions_data.keys())
    
    print(f"   Frontend attend l'ordre: {frontend_role_order}")
    print(f"   API retourne l'ordre: {api_role_order}")
    
    # 6. Test de la logique frontend
    print(f"\n6. SIMULATION LOGIQUE FRONTEND:")
    
    # Simuler ce que fait le frontend
    print(f"   Le frontend fait: rolePermissions[role.code]?.[permission.code] || false")
    
    if 'BASIC' in role_permissions_data:
        basic_data = role_permissions_data['BASIC']
        bilans_value = basic_data.get('bilans_financiers', False)
        print(f"   Pour BASIC + bilans_financiers:")
        print(f"     rolePermissions['BASIC']['bilans_financiers'] = {bilans_value}")
        print(f"     Résultat switch: {'✅ Activé' if bilans_value else '❌ Désactivé'}")
    else:
        print(f"   Pour BASIC + bilans_financiers:")
        print(f"     rolePermissions['BASIC'] = undefined")
        print(f"     Résultat switch: ❌ Undefined -> false")
    
    # 7. Générer un fichier de test pour le frontend
    print(f"\n7. GÉNÉRATION FICHIER TEST:")
    
    test_data = {
        "role_permissions": role_permissions_data,
        "debug_info": {
            "total_roles": len(role_permissions_data),
            "basic_present": 'BASIC' in role_permissions_data,
            "basic_permissions": role_permissions_data.get('BASIC', {}),
            "all_roles": list(role_permissions_data.keys())
        }
    }
    
    with open('frontend_test_data.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Fichier frontend_test_data.json créé")
    print(f"   Utilisez ce fichier pour tester le frontend localement")
    
    # 8. Recommandations
    print(f"\n8. RECOMMANDATIONS:")
    
    if 'BASIC' in role_permissions_data:
        print(f"   ✅ Les données backend sont correctes")
        print(f"   🔍 Le problème est probablement dans le frontend:")
        print(f"     - Vérifier la fonction loadRolePermissions()")
        print(f"     - Vérifier l'URL de l'API appelée")
        print(f"     - Vérifier les headers d'authentification")
        print(f"     - Vérifier la gestion des erreurs réseau")
    else:
        print(f"   ❌ Les données backend sont incorrectes")
        print(f"   🔧 Actions nécessaires:")
        print(f"     - Recréer les associations RolePermission pour BASIC")
        print(f"     - Vérifier que les permissions existent")

if __name__ == '__main__':
    debug_frontend_api()
