#!/usr/bin/env python
"""
Script pour créer TOUTES les permissions manquantes dans la base de données
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def create_all_permissions():
    """
    Crée toutes les permissions nécessaires dans la base de données
    """
    print("CREATION DE TOUTES LES PERMISSIONS")
    print("=" * 60)
    
    # Définir toutes les permissions nécessaires
    all_permissions = [
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
    existing_count = 0
    
    for perm_data in all_permissions:
        permission, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'category': perm_data['category'],
                'description': perm_data['description']
            }
        )
        
        if created:
            print(f"Crée: {perm_data['code']} - {perm_data['name']}")
            created_count += 1
        else:
            print(f"Existe: {perm_data['code']}")
            existing_count += 1
    
    print(f"\n📊 Résumé permissions:")
    print(f"   Permissions créées: {created_count}")
    print(f"   Permissions existantes: {existing_count}")
    print(f"   Total: {created_count + existing_count}")
    
    return created_count > 0

def assign_permissions_to_roles():
    """
    Assigne les permissions aux rôles appropriés
    """
    print(f"\nASSIGNATION PERMISSIONS AUX ROLES")
    print("=" * 60)
    
    # Définir les permissions par rôle
    role_permissions = {
        'CUSTOMER': [
            'dashboard.view', 'savings.view', 'savings.challenges', 
            'education.view', 'investments.view', 'support.create'
        ],
        'STUDENT': [
            'dashboard.view', 'education.view', 'education.create', 'support.create'
        ],
        'SGI_MANAGER': [
            'dashboard.view', 'sgi.view', 'sgi.manage', 'sgi.clients', 
            'investments.view', 'investments.manage'
        ],
        'INSTRUCTOR': [
            'dashboard.view', 'education.view', 'education.manage', 
            'education.create', 'support.respond'
        ],
        'SUPPORT': [
            'dashboard.view', 'support.tickets', 'support.respond', 
            'support.create', 'users.view'
        ],
        'ADMIN': [
            'dashboard.view', 'dashboard.admin', 'users.view', 'users.create', 
            'users.edit', 'users.delete', 'savings.view', 'savings.manage', 
            'education.view', 'education.manage', 'investments.view', 
            'investments.manage', 'sgi.view', 'sgi.manage', 'sgi.clients',
            'support.tickets', 'support.respond', 'support.create'
        ]
    }
    
    total_assigned = 0
    
    for role, permission_codes in role_permissions.items():
        print(f"\n📋 Rôle: {role}")
        role_assigned = 0
        
        for perm_code in permission_codes:
            try:
                permission = Permission.objects.get(code=perm_code)
                role_permission, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={'is_granted': True}
                )
                
                if created:
                    print(f"   Assignee: {perm_code}")
                    role_assigned += 1
                    total_assigned += 1
                elif not role_permission.is_granted:
                    role_permission.is_granted = True
                    role_permission.save()
                    print(f"   Activee: {perm_code}")
                    role_assigned += 1
                    total_assigned += 1
                else:
                    print(f"   Existe: {perm_code}")
                    
            except Permission.DoesNotExist:
                print(f"   Permission introuvable: {perm_code}")
        
        print(f"   Permissions pour {role}: {role_assigned} nouvelles/mises à jour")
    
    print(f"\n📊 Résumé assignations:")
    print(f"   Total assignations créées/mises à jour: {total_assigned}")
    
    return total_assigned

def verify_permissions():
    """
    Vérifie les permissions créées
    """
    print(f"\nVERIFICATION FINALE")
    print("=" * 60)
    
    # Compter les permissions par rôle
    roles = ['CUSTOMER', 'STUDENT', 'SGI_MANAGER', 'INSTRUCTOR', 'SUPPORT', 'ADMIN']
    
    for role in roles:
        count = RolePermission.objects.filter(role=role, is_granted=True).count()
        print(f"   {role}: {count} permissions accordées")
    
    # Vérifier spécifiquement dashboard.view pour CUSTOMER
    try:
        customer_dashboard = RolePermission.objects.get(
            role="CUSTOMER", 
            permission__code="dashboard.view",
            is_granted=True
        )
        print(f"\nCUSTOMER dashboard.view: ACCORDEE")
    except RolePermission.DoesNotExist:
        print(f"\nCUSTOMER dashboard.view: NON TROUVEE")

if __name__ == '__main__':
    print("INITIALISATION COMPLETE DU SYSTEME DE PERMISSIONS")
    print("=" * 60)
    
    # 1. Créer toutes les permissions
    permissions_created = create_all_permissions()
    
    # 2. Assigner aux rôles
    assignments_created = assign_permissions_to_roles()
    
    # 3. Vérifier
    verify_permissions()
    
    print(f"\n" + "=" * 60)
    print(f"SYSTEME DE PERMISSIONS INITIALISE")
    print(f"   Permissions créées: {permissions_created}")
    print(f"   Assignations créées: {assignments_created}")
    print(f"   Les switches devraient maintenant fonctionner pour tous les rôles")
    print("=" * 60)
