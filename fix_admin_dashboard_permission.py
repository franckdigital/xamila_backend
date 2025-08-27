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

def fix_admin_dashboard_permission():
    """Corriger le problème de la permission admin_dashboard"""
    
    print("=== CORRECTION PERMISSION ADMIN_DASHBOARD ===\n")
    
    # 1. Chercher la permission Dashboard Admin existante
    try:
        dashboard_perm = Permission.objects.get(name='Dashboard Admin')
        print(f"Permission trouvée: {dashboard_perm.name} (code: {dashboard_perm.code})")
        
        # Mettre à jour le code si nécessaire
        if dashboard_perm.code != 'admin_dashboard':
            old_code = dashboard_perm.code
            dashboard_perm.code = 'admin_dashboard'
            dashboard_perm.save()
            print(f"✅ Code mis à jour: {old_code} → admin_dashboard")
        else:
            print("✅ Code déjà correct: admin_dashboard")
            
    except Permission.DoesNotExist:
        # Créer la permission si elle n'existe pas
        dashboard_perm = Permission.objects.create(
            code='admin_dashboard',
            name='Dashboard Admin',
            category='Administration',
            description='Permission pour accéder au Dashboard Admin'
        )
        print(f"✅ Permission créée: {dashboard_perm}")
    
    # 2. Vérifier et créer l'association pour le rôle ADMIN
    admin_role_perm, created = RolePermission.objects.get_or_create(
        role='ADMIN',
        permission=dashboard_perm,
        defaults={'is_granted': True}
    )
    
    if created:
        print(f"✅ Association ADMIN → admin_dashboard créée")
    else:
        print(f"✅ Association ADMIN → admin_dashboard existe déjà")
    
    # 3. Vérifier le rôle BASIC
    print(f"\n=== VÉRIFICATION RÔLE BASIC ===")
    
    try:
        bilans_perm = Permission.objects.get(code='bilans_financiers')
        print(f"Permission bilans_financiers trouvée: {bilans_perm.name}")
        
        # Créer l'association BASIC → bilans_financiers
        basic_role_perm, created = RolePermission.objects.get_or_create(
            role='BASIC',
            permission=bilans_perm,
            defaults={'is_granted': True}
        )
        
        if created:
            print(f"✅ Association BASIC → bilans_financiers créée")
        else:
            print(f"✅ Association BASIC → bilans_financiers existe déjà")
            
    except Permission.DoesNotExist:
        print("❌ Permission bilans_financiers non trouvée")
    
    # 4. Résumé final
    print(f"\n=== RÉSUMÉ ===")
    
    # Compter les rôles
    roles = RolePermission.objects.values_list('role', flat=True).distinct()
    print(f"Rôles dans le système: {list(roles)}")
    
    # Vérifier BASIC
    basic_count = RolePermission.objects.filter(role='BASIC', is_granted=True).count()
    print(f"Permissions accordées au rôle BASIC: {basic_count}")
    
    # Vérifier ADMIN
    admin_count = RolePermission.objects.filter(role='ADMIN', is_granted=True).count()
    print(f"Permissions accordées au rôle ADMIN: {admin_count}")

if __name__ == '__main__':
    fix_admin_dashboard_permission()
