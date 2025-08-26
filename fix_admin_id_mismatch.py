#!/usr/bin/env python
"""
Script pour supprimer l'admin avec l'ID incorrect et créer celui avec l'ID du token JWT
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def fix_admin_id_mismatch():
    """
    Supprime l'admin avec l'ID incorrect et crée celui avec l'ID du token JWT
    """
    # ID incorrect créé par Postman
    wrong_admin_id = "2eba873b-ae5d-4ba6-ac33-df500fe9f88b"
    wrong_admin_email = "franckalain.digital1@gmail.com"
    
    # ID correct du token JWT
    correct_admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    correct_admin_email = "franckalain.digital@gmail.com"
    
    print("🔧 Correction de la discordance d'ID admin")
    print("=" * 60)
    
    # 1. Supprimer l'admin avec l'ID incorrect
    try:
        wrong_admin = User.objects.get(id=wrong_admin_id)
        print(f"❌ Suppression de l'admin incorrect:")
        print(f"   ID: {wrong_admin.id}")
        print(f"   Email: {wrong_admin.email}")
        
        # Supprimer les permissions associées
        RolePermission.objects.filter(role="ADMIN").delete()
        print(f"   Permissions admin supprimées")
        
        # Supprimer l'utilisateur
        wrong_admin.delete()
        print(f"   Utilisateur supprimé")
        
    except User.DoesNotExist:
        print(f"⚠️  Aucun admin trouvé avec l'ID incorrect")
    
    # 2. Créer l'admin avec l'ID correct
    try:
        # Vérifier si l'admin correct existe déjà
        correct_admin = User.objects.get(id=correct_admin_id)
        print(f"✅ Admin correct existe déjà:")
        print(f"   ID: {correct_admin.id}")
        print(f"   Email: {correct_admin.email}")
        
    except User.DoesNotExist:
        # Créer l'admin avec l'ID correct
        print(f"🔧 Création de l'admin avec l'ID correct:")
        print(f"   ID: {correct_admin_id}")
        print(f"   Email: {correct_admin_email}")
        
        correct_admin = User.objects.create_user(
            id=correct_admin_id,
            email=correct_admin_email,
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
        
        print(f"✅ Admin créé avec succès:")
        print(f"   ID: {correct_admin.id}")
        print(f"   Email: {correct_admin.email}")
        print(f"   Role: {correct_admin.role}")
    
    # 3. Créer les permissions par défaut
    create_default_permissions()
    
    # 4. Assigner toutes les permissions à l'admin
    assign_admin_permissions()
    
    print("\n" + "=" * 60)
    print("✅ CORRECTION TERMINÉE")
    print(f"   L'admin avec l'ID {correct_admin_id} est maintenant actif")
    print(f"   Le token JWT existant fonctionnera correctement")
    print("=" * 60)

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
        {'code': 'education.view', 'name': 'Voir Formation', 'category': 'Formation', 'description': 'Accéder aux contenus éducatifs'},
        {'code': 'education.manage', 'name': 'Gérer Formation', 'category': 'Formation', 'description': 'Administrer les formations'},
        {'code': 'education.create', 'name': 'Créer Formation', 'category': 'Formation', 'description': 'Créer du contenu éducatif'},
        {'code': 'investments.view', 'name': 'Voir Investissements', 'category': 'Investissement', 'description': 'Consulter les investissements'},
        {'code': 'investments.manage', 'name': 'Gérer Investissements', 'category': 'Investissement', 'description': 'Administrer les investissements'},
        {'code': 'sgi.view', 'name': 'Voir SGI', 'category': 'SGI', 'description': 'Consulter les SGI'},
        {'code': 'sgi.manage', 'name': 'Gérer SGI', 'category': 'SGI', 'description': 'Administrer les SGI'},
        {'code': 'sgi.clients', 'name': 'Clients SGI', 'category': 'SGI', 'description': 'Gérer les clients de la SGI'},
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
    
    print(f"🔑 Permissions assignées à l'admin: {assigned_count}")

if __name__ == '__main__':
    fix_admin_id_mismatch()
