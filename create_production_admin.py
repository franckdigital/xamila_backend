#!/usr/bin/env python
"""
Script pour créer l'utilisateur admin en production avec l'ID exact du token JWT
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def create_production_admin():
    """Crée l'utilisateur admin avec l'ID exact du token JWT"""
    
    # ID exact de l'utilisateur depuis le token JWT
    user_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    email = "franckalain.digital@gmail.com"
    username = "franckalain.digital"
    
    print(f"=== Création utilisateur admin en production ===")
    print(f"ID: {user_id}")
    print(f"Email: {email}")
    
    # Vérifier si l'utilisateur existe déjà
    try:
        user = User.objects.get(id=user_id)
        print(f"✓ Utilisateur existe déjà: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        return user
    except User.DoesNotExist:
        print("✗ Utilisateur n'existe pas - création en cours...")
    
    # Créer l'utilisateur admin
    try:
        user = User.objects.create_user(
            id=user_id,
            email=email,
            username=username,
            first_name="franck",
            last_name="alain",
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            password="XamilaAdmin2025!"  # Mot de passe sécurisé
        )
        print(f"✓ Utilisateur admin créé avec succès")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        return user
    except Exception as e:
        print(f"✗ Erreur lors de la création: {e}")
        return None

def create_permissions():
    """Crée les permissions par défaut"""
    
    permissions_data = [
        # Dashboard permissions
        {'name': 'Accès Dashboard', 'code': 'dashboard.view', 'category': 'Dashboard'},
        {'name': 'Dashboard Admin', 'code': 'dashboard.admin', 'category': 'Dashboard'},
        {'name': 'Dashboard SGI Manager', 'code': 'dashboard.sgi_manager', 'category': 'Dashboard'},
        {'name': 'Dashboard Instructor', 'code': 'dashboard.instructor', 'category': 'Dashboard'},
        {'name': 'Dashboard Support', 'code': 'dashboard.support', 'category': 'Dashboard'},
        
        # User management permissions
        {'name': 'Voir Utilisateurs', 'code': 'users.view', 'category': 'Gestion Utilisateurs'},
        {'name': 'Créer Utilisateur', 'code': 'users.create', 'category': 'Gestion Utilisateurs'},
        {'name': 'Modifier Utilisateur', 'code': 'users.edit', 'category': 'Gestion Utilisateurs'},
        {'name': 'Supprimer Utilisateur', 'code': 'users.delete', 'category': 'Gestion Utilisateurs'},
        {'name': 'Gérer Rôles', 'code': 'users.manage_roles', 'category': 'Gestion Utilisateurs'},
        
        # Admin permissions
        {'name': 'Gestion Permissions', 'code': 'admin.permissions', 'category': 'Administration'},
        {'name': 'Logs Système', 'code': 'admin.logs', 'category': 'Administration'},
        {'name': 'Configuration', 'code': 'admin.config', 'category': 'Administration'},
        
        # Challenges permissions
        {'name': 'Voir Challenges', 'code': 'challenges.view', 'category': 'Challenges'},
        {'name': 'Créer Challenge', 'code': 'challenges.create', 'category': 'Challenges'},
        {'name': 'Modifier Challenge', 'code': 'challenges.edit', 'category': 'Challenges'},
        {'name': 'Supprimer Challenge', 'code': 'challenges.delete', 'category': 'Challenges'},
    ]
    
    print("\n=== Création des permissions ===")
    created_count = 0
    
    for perm_data in permissions_data:
        try:
            permission, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'category': perm_data['category'],
                    'description': f"Permission pour {perm_data['name']}"
                }
            )
            if created:
                print(f"✓ Permission créée: {permission.name}")
                created_count += 1
            else:
                print(f"- Permission existe: {permission.name}")
        except Exception as e:
            print(f"✗ Erreur permission {perm_data['code']}: {e}")
    
    print(f"\nTotal permissions créées: {created_count}")
    return Permission.objects.all().count()

def assign_admin_permissions():
    """Assigne toutes les permissions à l'admin"""
    
    print("\n=== Assignation des permissions admin ===")
    permissions = Permission.objects.all()
    assigned_count = 0
    
    for permission in permissions:
        try:
            role_perm, created = RolePermission.objects.get_or_create(
                role='ADMIN',
                permission=permission,
                defaults={'is_granted': True}
            )
            if created:
                print(f"✓ ADMIN: {permission.name}")
                assigned_count += 1
            else:
                # Mettre à jour si pas accordée
                if not role_perm.is_granted:
                    role_perm.is_granted = True
                    role_perm.save()
                    print(f"↻ ADMIN: {permission.name} (mise à jour)")
                    assigned_count += 1
                else:
                    print(f"- ADMIN: {permission.name} (existe)")
        except Exception as e:
            print(f"✗ Erreur assignation {permission.code}: {e}")
    
    print(f"\nTotal permissions assignées: {assigned_count}")

if __name__ == '__main__':
    print("=== CRÉATION ADMIN PRODUCTION XAMILA ===")
    
    # Créer l'utilisateur admin
    admin_user = create_production_admin()
    
    if admin_user:
        # Créer les permissions
        total_permissions = create_permissions()
        
        # Assigner les permissions à l'admin
        assign_admin_permissions()
        
        print(f"\n=== RÉSUMÉ ===")
        print(f"✓ Utilisateur admin: {admin_user.email}")
        print(f"✓ ID: {admin_user.id}")
        print(f"✓ Role: {admin_user.role}")
        print(f"✓ Permissions totales: {total_permissions}")
        print(f"✓ Status: Prêt pour production")
        
        print(f"\n=== INSTRUCTIONS ===")
        print(f"1. L'utilisateur peut maintenant se connecter avec:")
        print(f"   Email: {admin_user.email}")
        print(f"   Mot de passe: XamilaAdmin2025!")
        print(f"2. Le token JWT existant devrait maintenant fonctionner")
        print(f"3. Toutes les permissions admin sont accordées")
    else:
        print("\n✗ Échec de la création de l'utilisateur admin")
        sys.exit(1)
