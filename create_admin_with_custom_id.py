#!/usr/bin/env python
"""
Script universel pour créer un admin avec un ID personnalisé
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def create_admin_with_custom_id(admin_id, email, username, first_name, last_name, password):
    """
    Crée un admin avec l'ID exact spécifié
    """
    print(f"🔧 Création admin avec ID personnalisé:")
    print(f"   ID: {admin_id}")
    print(f"   Email: {email}")
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.objects.get(id=admin_id)
        print(f"✅ Admin existe déjà avec cet ID:")
        print(f"   Email: {existing_user.email}")
        print(f"   Role: {existing_user.role}")
        return existing_user
        
    except User.DoesNotExist:
        # Créer l'admin avec l'ID personnalisé
        admin_user = User.objects.create_user(
            id=admin_id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            password=password
        )
        
        print(f"✅ Admin créé avec succès:")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        
        # Créer permissions et les assigner
        create_default_permissions()
        assign_admin_permissions()
        
        return admin_user

def create_default_permissions():
    """Crée les permissions par défaut"""
    permissions_data = [
        {'code': 'dashboard.view', 'name': 'Voir Dashboard', 'category': 'Dashboard', 'description': 'Accéder au tableau de bord'},
        {'code': 'dashboard.admin', 'name': 'Dashboard Admin', 'category': 'Dashboard', 'description': 'Accéder au dashboard administrateur'},
        {'code': 'users.view', 'name': 'Voir Utilisateurs', 'category': 'Gestion', 'description': 'Consulter la liste des utilisateurs'},
        {'code': 'users.create', 'name': 'Créer Utilisateurs', 'category': 'Gestion', 'description': 'Créer de nouveaux utilisateurs'},
        {'code': 'users.edit', 'name': 'Modifier Utilisateurs', 'category': 'Gestion', 'description': 'Modifier les utilisateurs existants'},
        {'code': 'users.delete', 'name': 'Supprimer Utilisateurs', 'category': 'Gestion', 'description': 'Supprimer des utilisateurs'},
        {'code': 'savings.view', 'name': 'Voir Épargne', 'category': 'Épargne', 'description': 'Consulter les données d\'épargne'},
        {'code': 'savings.manage', 'name': 'Gérer Épargne', 'category': 'Épargne', 'description': 'Administrer les comptes d\'épargne'},
        {'code': 'savings.challenges', 'name': 'Challenges Épargne', 'category': 'Épargne', 'description': 'Gérer les défis d\'épargne'},
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

def assign_admin_permissions():
    """Assigne toutes les permissions à l'admin"""
    permissions = Permission.objects.all()
    assigned_count = 0
    
    for permission in permissions:
        role_permission, created = RolePermission.objects.get_or_create(
            role="ADMIN",
            permission=permission,
            defaults={'is_granted': True}
        )
        if created or not role_permission.is_granted:
            role_permission.is_granted = True
            role_permission.save()
            assigned_count += 1
    
    print(f"🔑 Permissions assignées: {assigned_count}")

if __name__ == '__main__':
    # ID exact du token JWT
    ADMIN_ID = "30039510-2cc1-41b5-a483-b668513cd4e8"
    EMAIL = "franckalain.digital@gmail.com"
    USERNAME = "franckalain.digital"
    FIRST_NAME = "franck"
    LAST_NAME = "alain"
    PASSWORD = "XamilaAdmin2025!"
    
    print("🚀 Création admin avec ID du token JWT")
    print("=" * 60)
    
    admin = create_admin_with_custom_id(
        ADMIN_ID, EMAIL, USERNAME, FIRST_NAME, LAST_NAME, PASSWORD
    )
    
    print("\n" + "=" * 60)
    print("✅ SUCCÈS: Admin configuré avec l'ID exact")
    print(f"   Le token JWT fonctionnera maintenant")
    print("=" * 60)
