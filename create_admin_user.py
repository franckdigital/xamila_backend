#!/usr/bin/env python
"""
Script pour créer un utilisateur admin dans la base de données
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

def create_admin_user():
    """Crée l'utilisateur admin avec l'ID spécifique du token JWT"""
    
    # ID de l'utilisateur depuis le token JWT
    user_id = "74a5de49-eb85-48dc-9935-a5ae7e83cf2f"
    email = "franckalain.digital@gmail.com"
    username = "franckalain.digital"
    
    # Vérifier si l'utilisateur existe déjà
    try:
        user = User.objects.get(id=user_id)
        print(f"✓ Utilisateur existe déjà: {user.email}")
        return user
    except User.DoesNotExist:
        pass
    
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
            password="admin123"  # Mot de passe temporaire
        )
        print(f"✓ Utilisateur admin créé: {user.email}")
        return user
    except Exception as e:
        print(f"✗ Erreur lors de la création: {e}")
        return None

def create_default_permissions():
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
    ]
    
    print("Création des permissions...")
    for perm_data in permissions_data:
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
        else:
            print(f"- Permission existe: {permission.name}")

def assign_admin_permissions():
    """Assigne toutes les permissions à l'admin"""
    
    print("\nAssignation des permissions admin...")
    permissions = Permission.objects.all()
    
    for permission in permissions:
        role_perm, created = RolePermission.objects.get_or_create(
            role='ADMIN',
            permission=permission,
            defaults={'is_granted': True}
        )
        if created:
            print(f"✓ ADMIN: {permission.name}")
        else:
            print(f"- ADMIN: {permission.name} (existe)")

if __name__ == '__main__':
    print("=== Création utilisateur admin et permissions ===")
    
    # Créer l'utilisateur admin
    admin_user = create_admin_user()
    
    if admin_user:
        # Créer les permissions
        create_default_permissions()
        
        # Assigner les permissions à l'admin
        assign_admin_permissions()
        
        print(f"\n=== Terminé ===")
        print(f"Utilisateur admin: {admin_user.email}")
        print(f"ID: {admin_user.id}")
        print(f"Role: {admin_user.role}")
    else:
        print("Échec de la création de l'utilisateur admin")
