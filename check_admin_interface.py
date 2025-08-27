#!/usr/bin/env python
import os
import sys
import django

# Ajouter le répertoire du projet au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission
import json

def check_admin_interface():
    """Vérifier les données pour l'interface admin Django et dashboard"""
    
    print("=== VÉRIFICATION INTERFACE ADMIN ===\n")
    
    # 1. Simuler l'endpoint /api/admin/role-permissions/
    print("1. ENDPOINT /api/admin/role-permissions/ (pour dashboard admin):")
    
    # Récupérer toutes les permissions par rôle
    role_permissions_data = {}
    
    # Obtenir tous les rôles uniques
    roles = RolePermission.objects.values_list('role', flat=True).distinct().order_by('role')
    
    for role in roles:
        role_permissions_data[role] = {}
        role_perms = RolePermission.objects.filter(role=role).select_related('permission')
        
        for rp in role_perms:
            role_permissions_data[role][rp.permission.code] = rp.is_granted
    
    print("   Données retournées:")
    print(f"   - Rôles trouvés: {list(roles)}")
    
    # Vérifier spécifiquement BASIC
    if 'BASIC' in role_permissions_data:
        basic_perms = role_permissions_data['BASIC']
        print(f"   - BASIC permissions: {basic_perms}")
        if 'bilans_financiers' in basic_perms:
            print(f"   ✅ BASIC a bilans_financiers: {basic_perms['bilans_financiers']}")
        else:
            print(f"   ❌ BASIC n'a PAS bilans_financiers")
    else:
        print(f"   ❌ BASIC non trouvé dans role_permissions_data")
    
    # 2. Vérifier l'endpoint Django admin
    print(f"\n2. DJANGO ADMIN INTERFACE:")
    
    # Simuler ce que voit l'admin Django
    print("   Permissions dans core_permission:")
    permissions = Permission.objects.all().order_by('category', 'name')
    
    bilans_found = False
    for perm in permissions:
        if perm.code == 'bilans_financiers':
            print(f"   ✅ bilans_financiers trouvé: {perm.name} (ID: {perm.id})")
            bilans_found = True
    
    if not bilans_found:
        print(f"   ❌ bilans_financiers NON trouvé dans les permissions")
    
    print(f"\n   Associations dans core_rolepermission:")
    role_perms = RolePermission.objects.all().order_by('role')
    
    basic_associations = []
    for rp in role_perms:
        if rp.role == 'BASIC':
            basic_associations.append({
                'permission': rp.permission.code,
                'name': rp.permission.name,
                'granted': rp.is_granted
            })
    
    if basic_associations:
        print(f"   ✅ BASIC associations trouvées:")
        for assoc in basic_associations:
            status = "✅ Accordée" if assoc['granted'] else "❌ Refusée"
            print(f"      - {assoc['permission']} ({assoc['name']}) - {status}")
    else:
        print(f"   ❌ Aucune association BASIC trouvée")
    
    # 3. Vérifier les URLs et vues
    print(f"\n3. VÉRIFICATION DES ENDPOINTS:")
    
    # Simuler l'appel API pour le dashboard admin
    try:
        from core.views_permissions import RolePermissionsManagementView
        print(f"   ✅ RolePermissionsManagementView disponible")
        
        # Vérifier si la vue retourne les bonnes données
        all_role_perms = RolePermission.objects.all().select_related('permission')
        print(f"   - Total RolePermissions: {all_role_perms.count()}")
        
        basic_count = all_role_perms.filter(role='BASIC').count()
        print(f"   - BASIC RolePermissions: {basic_count}")
        
    except Exception as e:
        print(f"   ❌ Erreur avec RolePermissionsManagementView: {e}")
    
    # 4. Format JSON pour le dashboard admin
    print(f"\n4. FORMAT JSON POUR DASHBOARD ADMIN:")
    
    api_response = {
        "role_permissions": role_permissions_data
    }
    
    print(f"   Structure de réponse:")
    print(f"   - Clés principales: {list(api_response.keys())}")
    print(f"   - Rôles dans role_permissions: {list(api_response['role_permissions'].keys())}")
    
    if 'BASIC' in api_response['role_permissions']:
        basic_data = api_response['role_permissions']['BASIC']
        print(f"   - BASIC data: {basic_data}")
    
    # 5. Recommandations
    print(f"\n5. RECOMMANDATIONS:")
    
    if 'BASIC' not in roles:
        print(f"   ❌ Créer des associations RolePermission pour BASIC")
    
    if not bilans_found:
        print(f"   ❌ Créer la permission bilans_financiers")
    
    if 'BASIC' in role_permissions_data and 'bilans_financiers' in role_permissions_data['BASIC']:
        print(f"   ✅ Configuration correcte - BASIC devrait apparaître")
    else:
        print(f"   ❌ Configuration incorrecte - BASIC n'apparaîtra pas")

if __name__ == '__main__':
    check_admin_interface()
