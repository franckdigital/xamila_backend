#!/usr/bin/env python
"""
Script pour créer les permissions manquantes pour le rôle CUSTOMER
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def create_customer_permissions():
    """
    Crée les permissions pour le rôle CUSTOMER
    """
    print("🔧 CRÉATION PERMISSIONS CUSTOMER")
    print("=" * 50)
    
    # Permissions que CUSTOMER doit avoir
    customer_permissions = [
        'dashboard.view',
        'savings.view',
        'savings.challenges',
        'education.view',
        'investments.view',
        'support.create'
    ]
    
    created_count = 0
    
    for perm_code in customer_permissions:
        try:
            # Récupérer la permission
            permission = Permission.objects.get(code=perm_code)
            
            # Créer ou récupérer la RolePermission pour CUSTOMER
            role_permission, created = RolePermission.objects.get_or_create(
                role="CUSTOMER",
                permission=permission,
                defaults={'is_granted': True}
            )
            
            if created:
                print(f"✅ Créé: CUSTOMER | {perm_code}")
                created_count += 1
            else:
                # Vérifier si elle est accordée
                if not role_permission.is_granted:
                    role_permission.is_granted = True
                    role_permission.save()
                    print(f"🔄 Mise à jour: CUSTOMER | {perm_code}")
                    created_count += 1
                else:
                    print(f"✓ Existe: CUSTOMER | {perm_code}")
                    
        except Permission.DoesNotExist:
            print(f"❌ Permission non trouvée: {perm_code}")
    
    print(f"\n📊 Résumé:")
    print(f"   Permissions traitées: {len(customer_permissions)}")
    print(f"   Permissions créées/mises à jour: {created_count}")
    
    # Vérifier le résultat
    print(f"\n🔍 Vérification:")
    customer_perms = RolePermission.objects.filter(role="CUSTOMER", is_granted=True)
    print(f"   Total permissions CUSTOMER: {customer_perms.count()}")
    
    for rp in customer_perms:
        print(f"   - {rp.permission.code}: ✅")

def create_all_role_permissions():
    """
    Crée les permissions pour tous les rôles
    """
    print(f"\n🔧 CRÉATION PERMISSIONS TOUS RÔLES")
    print("=" * 50)
    
    # Définir les permissions par rôle
    role_permissions = {
        'CUSTOMER': ['dashboard.view', 'savings.view', 'savings.challenges', 'education.view', 'investments.view', 'support.create'],
        'STUDENT': ['dashboard.view', 'education.view', 'education.create', 'support.create'],
        'SGI_MANAGER': ['dashboard.view', 'sgi.view', 'sgi.manage', 'sgi.clients', 'investments.view', 'investments.manage'],
        'INSTRUCTOR': ['dashboard.view', 'education.view', 'education.manage', 'education.create', 'support.respond'],
        'SUPPORT': ['dashboard.view', 'support.tickets', 'support.respond', 'support.create', 'users.view'],
        'ADMIN': ['dashboard.view', 'dashboard.admin', 'users.view', 'users.create', 'users.edit', 'users.delete', 
                 'savings.view', 'savings.manage', 'education.view', 'education.manage', 'investments.view', 
                 'investments.manage', 'sgi.view', 'sgi.manage', 'support.tickets', 'support.respond']
    }
    
    total_created = 0
    
    for role, permissions in role_permissions.items():
        print(f"\n📋 Rôle: {role}")
        role_created = 0
        
        for perm_code in permissions:
            try:
                permission = Permission.objects.get(code=perm_code)
                role_permission, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={'is_granted': True}
                )
                
                if created:
                    print(f"   ✅ {perm_code}")
                    role_created += 1
                    total_created += 1
                elif not role_permission.is_granted:
                    role_permission.is_granted = True
                    role_permission.save()
                    print(f"   🔄 {perm_code}")
                    role_created += 1
                    total_created += 1
                    
            except Permission.DoesNotExist:
                print(f"   ❌ Permission manquante: {perm_code}")
        
        print(f"   Créées/mises à jour: {role_created}")
    
    print(f"\n📊 RÉSUMÉ GLOBAL:")
    print(f"   Total permissions créées/mises à jour: {total_created}")

if __name__ == '__main__':
    # Créer d'abord les permissions pour CUSTOMER
    create_customer_permissions()
    
    # Puis pour tous les rôles
    create_all_role_permissions()
    
    print(f"\n" + "=" * 50)
    print(f"✅ TOUTES LES PERMISSIONS CONFIGURÉES")
    print(f"   Les switches devraient maintenant fonctionner pour tous les rôles")
    print("=" * 50)
