#!/usr/bin/env python
import os
import sys
import django

# Ajouter le répertoire du projet au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def create_default_permissions():
    """Crée les permissions par défaut du système"""
    
    # Définir les permissions par catégorie
    permissions_data = [
        # Services Financiers
        {'name': 'Plans Épargne', 'code': 'savings_plans', 'category': 'Services Financiers'},
        {'name': 'Formation Bourse', 'code': 'trading_education', 'category': 'Services Financiers'},
        {'name': 'Mon Portefeuille', 'code': 'portfolio', 'category': 'Services Financiers'},
        {'name': 'Mes SGI', 'code': 'my_sgi', 'category': 'Services Financiers'},
        {'name': 'Ma Caisse', 'code': 'ma_caisse', 'category': 'Services Financiers'},
        {'name': 'Défis Épargne', 'code': 'savings_challenge', 'category': 'Services Financiers'},
        {'name': 'Bilans Financiers', 'code': 'bilans_financiers', 'category': 'Services Financiers'},
        
        # Gestion
        {'name': 'Gestion Utilisateurs', 'code': 'user_management', 'category': 'Gestion'},
        {'name': 'Gestion SGI', 'code': 'sgi_management', 'category': 'Gestion'},
        {'name': 'Gestion Contrats', 'code': 'contract_management', 'category': 'Gestion'},
        {'name': 'Gestion Clients', 'code': 'client_management', 'category': 'Gestion'},
        
        # Formation
        {'name': 'Mes Cours', 'code': 'my_courses', 'category': 'Formation'},
        {'name': 'Formations', 'code': 'learning', 'category': 'Formation'},
        {'name': 'Quiz & Tests', 'code': 'quizzes', 'category': 'Formation'},
        {'name': 'Certificats', 'code': 'certificates', 'category': 'Formation'},
        {'name': 'Progression', 'code': 'progress', 'category': 'Formation'},
        
        # Support
        {'name': 'Tickets', 'code': 'tickets', 'category': 'Support'},
        {'name': 'Rapports', 'code': 'reports', 'category': 'Support'},
        {'name': 'Statistiques', 'code': 'analytics', 'category': 'Support'},
        
        # Administration
        {'name': 'Dashboard Admin', 'code': 'admin_dashboard', 'category': 'Administration'},
        {'name': 'Gestion Rôles', 'code': 'role_management', 'category': 'Administration'},
        {'name': 'Sécurité', 'code': 'security', 'category': 'Administration'},
        {'name': 'Notifications', 'code': 'notifications', 'category': 'Administration'},
    ]
    
    # Créer les permissions
    created_permissions = []
    for perm_data in permissions_data:
        permission, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'category': perm_data['category'],
                'description': f"Permission pour accéder à {perm_data['name']}"
            }
        )
        if created:
            created_permissions.append(permission)
            print(f"Créé: {permission}")
    
    # Définir les permissions par rôle
    role_permissions = {
        'CUSTOMER': [
            'savings_plans', 'trading_education', 'portfolio', 'my_sgi', 
            'ma_caisse', 'savings_challenge', 'bilans_financiers'
        ],
        'BASIC': [
            'bilans_financiers'
        ],
        'SGI_MANAGER': [
            'sgi_management', 'contract_management', 'client_management',
            'my_courses', 'reports'
        ],
        'INSTRUCTOR': [
            'my_courses', 'learning', 'quizzes', 'certificates', 'progress'
        ],
        'STUDENT': [
            'my_courses', 'learning', 'quizzes', 'certificates', 'progress'
        ],
        'SUPPORT': [
            'tickets', 'reports', 'analytics', 'user_management'
        ],
        'ADMIN': [
            # Les admins ont toutes les permissions
            perm['code'] for perm in permissions_data
        ]
    }
    
    # Créer les associations rôle-permission
    created_role_perms = 0
    for role, perm_codes in role_permissions.items():
        for perm_code in perm_codes:
            try:
                permission = Permission.objects.get(code=perm_code)
                role_perm, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={'is_granted': True}
                )
                if created:
                    created_role_perms += 1
            except Permission.DoesNotExist:
                print(f"ATTENTION: Permission {perm_code} non trouvée pour le rôle {role}")
    
    print(f"\n✅ SUCCÈS:")
    print(f"- Permissions créées: {len(created_permissions)}")
    print(f"- Associations rôle-permission créées: {created_role_perms}")
    print(f"- Rôle BASIC configuré avec permission 'bilans_financiers'")

if __name__ == '__main__':
    create_default_permissions()
