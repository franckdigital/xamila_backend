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

def debug_roles_permissions():
    """Debug des rôles et permissions dans la base de données"""
    
    print("=== DEBUG PERMISSIONS ET RÔLES ===\n")
    
    # 1. Vérifier toutes les permissions
    print("1. TOUTES LES PERMISSIONS:")
    permissions = Permission.objects.all().order_by('category', 'name')
    for perm in permissions:
        print(f"   - {perm.category} | {perm.code} | {perm.name}")
    
    # 2. Vérifier bilans_financiers spécifiquement
    print(f"\n2. PERMISSION BILANS_FINANCIERS:")
    try:
        bilans_perm = Permission.objects.get(code='bilans_financiers')
        print(f"   ✅ Trouvée: {bilans_perm.name} (ID: {bilans_perm.id})")
    except Permission.DoesNotExist:
        print("   ❌ Permission bilans_financiers NON TROUVÉE")
    
    # 3. Vérifier tous les rôles dans RolePermission
    print(f"\n3. TOUS LES RÔLES DANS ROLEPERMISSION:")
    roles = RolePermission.objects.values_list('role', flat=True).distinct().order_by('role')
    for role in roles:
        print(f"   - {role}")
    
    # 4. Vérifier le rôle BASIC spécifiquement
    print(f"\n4. RÔLE BASIC:")
    basic_perms = RolePermission.objects.filter(role='BASIC')
    if basic_perms.exists():
        print(f"   ✅ Rôle BASIC trouvé avec {basic_perms.count()} permissions:")
        for rp in basic_perms:
            status = "✅ Accordée" if rp.is_granted else "❌ Refusée"
            print(f"      - {rp.permission.code} ({rp.permission.name}) - {status}")
    else:
        print("   ❌ Rôle BASIC NON TROUVÉ dans RolePermission")
    
    # 5. Vérifier admin_dashboard
    print(f"\n5. PERMISSION ADMIN_DASHBOARD:")
    try:
        admin_dash_perm = Permission.objects.get(code='admin_dashboard')
        print(f"   ✅ Trouvée: {admin_dash_perm.name} (ID: {admin_dash_perm.id})")
        
        # Vérifier si elle est assignée au rôle ADMIN
        admin_has_dashboard = RolePermission.objects.filter(
            role='ADMIN', 
            permission=admin_dash_perm
        ).exists()
        print(f"   ADMIN a cette permission: {'✅ OUI' if admin_has_dashboard else '❌ NON'}")
        
    except Permission.DoesNotExist:
        print("   ❌ Permission admin_dashboard NON TROUVÉE")
        # Chercher par nom
        try:
            dashboard_perms = Permission.objects.filter(name__icontains='Dashboard')
            print(f"   Permissions contenant 'Dashboard':")
            for perm in dashboard_perms:
                print(f"      - {perm.code} | {perm.name}")
        except:
            pass
    
    # 6. Compter les permissions par rôle
    print(f"\n6. NOMBRE DE PERMISSIONS PAR RÔLE:")
    for role in roles:
        count = RolePermission.objects.filter(role=role, is_granted=True).count()
        print(f"   - {role}: {count} permissions")

if __name__ == '__main__':
    debug_roles_permissions()
