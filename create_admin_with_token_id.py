#!/usr/bin/env python
"""
Script pour créer l'utilisateur admin avec l'ID exact du token JWT
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def create_admin_with_token_id():
    """
    Crée l'utilisateur admin avec l'ID exact du token JWT
    """
    # ID exact du token JWT
    admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    admin_email = "franckalain.digital@gmail.com"
    
    print(f"🔧 Création de l'utilisateur admin avec ID du token...")
    print(f"   ID: {admin_id}")
    print(f"   Email: {admin_email}")
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.objects.get(id=admin_id)
        print(f"✅ Utilisateur existe déjà:")
        print(f"   Email: {existing_user.email}")
        print(f"   Role: {existing_user.role}")
        print(f"   Actif: {existing_user.is_active}")
        return existing_user
        
    except User.DoesNotExist:
        # Créer l'utilisateur admin
        admin_user = User.objects.create_user(
            id=admin_id,
            email=admin_email,
            username="franckalain.digital",
            first_name="franck",
            last_name="alain",
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            password="XamilaAdmin2025!"
        )
        
        print(f"✅ Utilisateur admin créé avec succès:")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Staff: {admin_user.is_staff}")
        print(f"   Superuser: {admin_user.is_superuser}")
        
        # Créer les permissions par défaut si elles n'existent pas
        create_default_permissions()
        
        # Assigner toutes les permissions à l'admin
        assign_admin_permissions(admin_user)
        
        return admin_user

def create_default_permissions():
    """
    Crée les permissions par défaut
    """
    permissions_data = [
        # Dashboard permissions
        {'code': 'dashboard.view', 'name': 'Voir Dashboard', 'category': 'Dashboard', 'description': 'Accéder au tableau de bord'},
        {'code': 'dashboard.admin', 'name': 'Dashboard Admin', 'category': 'Dashboard', 'description': 'Accéder au dashboard administrateur'},
        
        # User management permissions
        {'code': 'users.view', 'name': 'Voir Utilisateurs', 'category': 'Gestion', 'description': 'Consulter la liste des utilisateurs'},
        {'code': 'users.create', 'name': 'Créer Utilisateurs', 'category': 'Gestion', 'description': 'Créer de nouveaux utilisateurs'},
        {'code': 'users.edit', 'name': 'Modifier Utilisateurs', 'category': 'Gestion', 'description': 'Modifier les utilisateurs existants'},
        {'code': 'users.delete', 'name': 'Supprimer Utilisateurs', 'category': 'Gestion', 'description': 'Supprimer des utilisateurs'},
        
        # Savings permissions
        {'code': 'savings.view', 'name': 'Voir Épargne', 'category': 'Épargne', 'description': 'Consulter les données d\'épargne'},
        {'code': 'savings.manage', 'name': 'Gérer Épargne', 'category': 'Épargne', 'description': 'Administrer les comptes d\'épargne'},
        {'code': 'savings.challenges', 'name': 'Challenges Épargne', 'category': 'Épargne', 'description': 'Gérer les défis d\'épargne'},
        
        # Education permissions
        {'code': 'education.view', 'name': 'Voir Formation', 'category': 'Formation', 'description': 'Accéder aux contenus éducatifs'},
        {'code': 'education.manage', 'name': 'Gérer Formation', 'category': 'Formation', 'description': 'Administrer les formations'},
        {'code': 'education.create', 'name': 'Créer Formation', 'category': 'Formation', 'description': 'Créer du contenu éducatif'},
        
        # Investment permissions
        {'code': 'investments.view', 'name': 'Voir Investissements', 'category': 'Investissement', 'description': 'Consulter les investissements'},
        {'code': 'investments.manage', 'name': 'Gérer Investissements', 'category': 'Investissement', 'description': 'Administrer les investissements'},
        
        # SGI permissions
        {'code': 'sgi.view', 'name': 'Voir SGI', 'category': 'SGI', 'description': 'Consulter les SGI'},
        {'code': 'sgi.manage', 'name': 'Gérer SGI', 'category': 'SGI', 'description': 'Administrer les SGI'},
        {'code': 'sgi.clients', 'name': 'Clients SGI', 'category': 'SGI', 'description': 'Gérer les clients de la SGI'},
        
        # Support permissions
        {'code': 'support.tickets', 'name': 'Tickets Support', 'category': 'Support', 'description': 'Gérer les tickets de support'},
        {'code': 'support.respond', 'name': 'Répondre Support', 'category': 'Support', 'description': 'Répondre aux demandes de support'},
        {'code': 'support.create', 'name': 'Créer Tickets Support', 'category': 'Support', 'description': 'Créer des tickets de support'}
    ]
    
    created_count = 0
    for perm_data in permissions_data:
        permission, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'category': perm_data['category'],
                'description': perm_data['description']
            }
        )
        if created:
            created_count += 1
    
    print(f"📋 Permissions créées: {created_count}/{len(permissions_data)}")

def assign_admin_permissions(admin_user):
    """
    Assigne toutes les permissions à l'admin
    """
    permissions = Permission.objects.all()
    assigned_count = 0
    
    for permission in permissions:
        role_permission, created = RolePermission.objects.get_or_create(
            role="ADMIN",
            permission=permission,
            defaults={'is_granted': True}
        )
        if created:
            assigned_count += 1
        elif not role_permission.is_granted:
            role_permission.is_granted = True
            role_permission.save()
            assigned_count += 1
    
    print(f"🔑 Permissions assignées à l'admin: {assigned_count}")

if __name__ == '__main__':
    print("🚀 Création de l'utilisateur admin avec ID du token JWT")
    print("=" * 60)
    
    admin_user = create_admin_with_token_id()
    
    print("\n" + "=" * 60)
    print("✅ SUCCÈS: Utilisateur admin configuré")
    print(f"   Le token JWT existant fonctionnera maintenant")
    print(f"   ID utilisateur: {admin_user.id}")
    print(f"   Email: {admin_user.email}")
    print("=" * 60)
