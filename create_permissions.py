#!/usr/bin/env python
"""
Script pour créer les permissions par défaut dans la base de données SQLite
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

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
        
        # Savings permissions
        {'name': 'Plans Épargne', 'code': 'savings.plans', 'category': 'Épargne'},
        {'name': 'Défis Épargne', 'code': 'savings.challenges', 'category': 'Épargne'},
        {'name': 'Gérer Épargne', 'code': 'savings.manage', 'category': 'Épargne'},
        
        # Portfolio permissions
        {'name': 'Voir Portfolio', 'code': 'portfolio.view', 'category': 'Portfolio'},
        {'name': 'Gérer Portfolio', 'code': 'portfolio.manage', 'category': 'Portfolio'},
        
        # SGI permissions
        {'name': 'Voir SGI', 'code': 'sgi.view', 'category': 'SGI'},
        {'name': 'Gérer SGI', 'code': 'sgi.manage', 'category': 'SGI'},
        {'name': 'Clients SGI', 'code': 'sgi.clients', 'category': 'SGI'},
        
        # Training permissions
        {'name': 'Formation Bourse', 'code': 'training.bourse', 'category': 'Formation'},
        {'name': 'Créer Formation', 'code': 'training.create', 'category': 'Formation'},
        {'name': 'Gérer Formation', 'code': 'training.manage', 'category': 'Formation'},
        
        # Support permissions
        {'name': 'Tickets Support', 'code': 'support.tickets', 'category': 'Support'},
        {'name': 'Répondre Support', 'code': 'support.respond', 'category': 'Support'},
        
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

def create_default_role_permissions():
    """Crée les permissions par défaut pour chaque rôle"""
    
    role_permissions = {
        'CUSTOMER': [
            'dashboard.view', 'savings.plans', 'savings.challenges', 
            'portfolio.view', 'training.bourse'
        ],
        'SGI_MANAGER': [
            'dashboard.view', 'dashboard.sgi_manager', 'sgi.view', 
            'sgi.manage', 'sgi.clients', 'users.view'
        ],
        'INSTRUCTOR': [
            'dashboard.view', 'dashboard.instructor', 'training.bourse',
            'training.create', 'training.manage'
        ],
        'SUPPORT': [
            'dashboard.view', 'dashboard.support', 'support.tickets',
            'support.respond', 'users.view'
        ],
        'ADMIN': [
            # Admin a toutes les permissions
            perm.code for perm in Permission.objects.all()
        ]
    }
    
    print("\nCréation des permissions de rôles...")
    for role, permission_codes in role_permissions.items():
        for perm_code in permission_codes:
            try:
                permission = Permission.objects.get(code=perm_code)
                role_perm, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={'is_granted': True}
                )
                if created:
                    print(f"✓ {role}: {permission.name}")
                else:
                    print(f"- {role}: {permission.name} (existe)")
            except Permission.DoesNotExist:
                print(f"✗ Permission non trouvée: {perm_code}")

if __name__ == '__main__':
    print("=== Création des permissions par défaut ===")
    create_default_permissions()
    create_default_role_permissions()
    print("\n=== Terminé ===")
