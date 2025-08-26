#!/usr/bin/env python
"""
Script pour corriger l'ID admin - différence d'un caractère détectée
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def fix_admin_id_exact():
    """
    Corrige l'ID admin - différence détectée entre token JWT et admin créé
    """
    # ID dans le token JWT (correct)
    correct_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    # ID de l'admin créé (incorrect - différence d'un caractère à la fin)
    wrong_id = "30039510-2cc1-41b5-a483-b668513cd4e9"
    
    print("🔧 CORRECTION ID ADMIN")
    print("=" * 60)
    print(f"ID Token JWT (correct): {correct_id}")
    print(f"ID Admin créé (wrong):  {wrong_id}")
    print(f"Différence détectée:    Dernier caractère (8 vs 9)")
    
    # 1. Supprimer l'admin avec l'ID incorrect
    try:
        wrong_admin = User.objects.get(id=wrong_id)
        print(f"\n❌ Suppression admin avec ID incorrect:")
        print(f"   Email: {wrong_admin.email}")
        print(f"   Username: {wrong_admin.username}")
        
        # Supprimer les permissions associées à cet admin spécifiquement
        # (on garde les permissions générales ADMIN pour le nouvel admin)
        wrong_admin.delete()
        print(f"   ✅ Admin supprimé")
        
    except User.DoesNotExist:
        print(f"\n⚠️  Aucun admin trouvé avec l'ID incorrect")
    
    # 2. Créer l'admin avec l'ID exact du token JWT
    try:
        correct_admin = User.objects.get(id=correct_id)
        print(f"\n✅ Admin avec ID correct existe déjà:")
        print(f"   Email: {correct_admin.email}")
        
    except User.DoesNotExist:
        print(f"\n🔧 Création admin avec ID exact du token JWT:")
        
        correct_admin = User.objects.create_user(
            id=correct_id,
            email="franckalain.digital@gmail.com",
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
        
        print(f"   ✅ Admin créé:")
        print(f"   ID: {correct_admin.id}")
        print(f"   Email: {correct_admin.email}")
    
    # 3. Vérifier et créer les permissions
    create_default_permissions()
    assign_admin_permissions()
    
    print(f"\n" + "=" * 60)
    print(f"✅ CORRECTION TERMINÉE")
    print(f"   ID exact du token JWT: {correct_id}")
    print(f"   Admin configuré avec cet ID exact")
    print(f"   Les switches de permissions fonctionneront maintenant")
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
    
    print(f"🔑 Permissions assignées: {assigned_count}")

if __name__ == '__main__':
    fix_admin_id_exact()
