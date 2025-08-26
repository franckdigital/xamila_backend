#!/usr/bin/env python
"""
Script pour diagnostiquer les permissions de l'admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def debug_admin_permissions():
    """
    Diagnostique les permissions de l'admin avec l'ID correct
    """
    admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    print("🔍 DIAGNOSTIC PERMISSIONS ADMIN")
    print("=" * 60)
    
    # 1. Vérifier l'admin
    try:
        admin = User.objects.get(id=admin_id)
        print(f"✅ Admin trouvé:")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Active: {admin.is_active}")
        print(f"   Staff: {admin.is_staff}")
        print(f"   Superuser: {admin.is_superuser}")
        
    except User.DoesNotExist:
        print(f"❌ Aucun admin trouvé avec l'ID: {admin_id}")
        return
    
    # 2. Vérifier les permissions existantes
    permissions = Permission.objects.all()
    print(f"\n📋 Permissions dans la base: {permissions.count()}")
    for perm in permissions:
        print(f"   - {perm.code}: {perm.name}")
    
    # 3. Vérifier les permissions assignées à ADMIN
    admin_permissions = RolePermission.objects.filter(role="ADMIN")
    print(f"\n🔑 Permissions assignées au rôle ADMIN: {admin_permissions.count()}")
    
    granted_count = 0
    for role_perm in admin_permissions:
        status = "✅ ACCORDÉE" if role_perm.is_granted else "❌ REFUSÉE"
        print(f"   - {role_perm.permission.code}: {status}")
        if role_perm.is_granted:
            granted_count += 1
    
    print(f"\n📊 Résumé:")
    print(f"   Total permissions: {permissions.count()}")
    print(f"   Permissions ADMIN: {admin_permissions.count()}")
    print(f"   Permissions accordées: {granted_count}")
    
    # 4. Créer les permissions manquantes si nécessaire
    if permissions.count() == 0:
        print(f"\n🔧 Création des permissions par défaut...")
        create_default_permissions()
        assign_admin_permissions()
        print(f"✅ Permissions créées et assignées")
    
    # 5. Vérifier une permission spécifique (dashboard.view)
    try:
        dashboard_perm = RolePermission.objects.get(
            role="ADMIN", 
            permission__code="dashboard.view"
        )
        print(f"\n🎯 Permission 'dashboard.view' pour ADMIN:")
        print(f"   Accordée: {dashboard_perm.is_granted}")
        print(f"   Créée le: {dashboard_perm.created_at}")
        print(f"   Modifiée le: {dashboard_perm.updated_at}")
        
    except RolePermission.DoesNotExist:
        print(f"\n❌ Permission 'dashboard.view' non trouvée pour ADMIN")
        
        # Créer la permission manquante
        try:
            perm = Permission.objects.get(code="dashboard.view")
            role_perm = RolePermission.objects.create(
                role="ADMIN",
                permission=perm,
                is_granted=True
            )
            print(f"✅ Permission 'dashboard.view' créée pour ADMIN")
        except Permission.DoesNotExist:
            print(f"❌ Permission 'dashboard.view' n'existe pas dans la base")

def create_default_permissions():
    """Crée les permissions par défaut"""
    permissions_data = [
        {'code': 'dashboard.view', 'name': 'Voir Dashboard', 'category': 'Dashboard', 'description': 'Accéder au tableau de bord'},
        {'code': 'dashboard.admin', 'name': 'Dashboard Admin', 'category': 'Dashboard', 'description': 'Accéder au dashboard administrateur'},
        {'code': 'users.view', 'name': 'Voir Utilisateurs', 'category': 'Gestion', 'description': 'Consulter la liste des utilisateurs'},
        {'code': 'users.create', 'name': 'Créer Utilisateurs', 'category': 'Gestion', 'description': 'Créer de nouveaux utilisateurs'},
        {'code': 'users.edit', 'name': 'Modifier Utilisateurs', 'category': 'Gestion', 'description': 'Modifier les utilisateurs existants'},
        {'code': 'users.delete', 'name': 'Supprimer Utilisateurs', 'category': 'Gestion', 'description': 'Supprimer des utilisateurs'},
    ]
    
    for perm_data in permissions_data:
        Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'category': perm_data['category'],
                'description': perm_data['description']
            }
        )

def assign_admin_permissions():
    """Assigne toutes les permissions à l'admin"""
    permissions = Permission.objects.all()
    
    for permission in permissions:
        RolePermission.objects.get_or_create(
            role="ADMIN",
            permission=permission,
            defaults={'is_granted': True}
        )

if __name__ == '__main__':
    debug_admin_permissions()
