#!/usr/bin/env python
"""
Script pour analyser les codes de permissions en base vs frontend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def analyze_permission_codes():
    """
    Analyser les codes de permissions
    """
    print("ANALYSE DES CODES DE PERMISSIONS")
    print("=" * 50)
    
    # Codes utilisés dans le frontend
    frontend_codes = [
        'dashboard.view', 'dashboard.admin', 'dashboard.sgi_manager', 
        'dashboard.instructor', 'dashboard.support',
        'savings.plans', 'savings.challenges', 'portfolio.view', 'sgi.access',
        'training.bourse', 'training.create', 'training.manage',
        'users.view', 'users.create', 'users.edit', 'users.delete',
        'sgi.view', 'sgi.manage', 'sgi.clients',
        'support.tickets', 'support.respond', 'support.create'
    ]
    
    # Codes en base de données
    db_permissions = Permission.objects.all()
    db_codes = [p.code for p in db_permissions]
    
    print("CODES FRONTEND:")
    for code in sorted(frontend_codes):
        print(f"  - {code}")
    
    print(f"\nCODES BASE DE DONNEES:")
    for code in sorted(db_codes):
        print(f"  - {code}")
    
    print(f"\nCOMPARAISON:")
    
    # Codes frontend manquants en base
    missing_in_db = set(frontend_codes) - set(db_codes)
    if missing_in_db:
        print(f"\nCodes FRONTEND manquants en BASE:")
        for code in sorted(missing_in_db):
            print(f"  ❌ {code}")
    
    # Codes base manquants en frontend
    missing_in_frontend = set(db_codes) - set(frontend_codes)
    if missing_in_frontend:
        print(f"\nCodes BASE manquants en FRONTEND:")
        for code in sorted(missing_in_frontend):
            print(f"  ⚠️  {code}")
    
    # Codes qui correspondent
    matching_codes = set(frontend_codes) & set(db_codes)
    print(f"\nCodes qui CORRESPONDENT ({len(matching_codes)}):")
    for code in sorted(matching_codes):
        print(f"  ✅ {code}")
    
    print(f"\nPERMISSIONS CUSTOMER:")
    customer_perms = RolePermission.objects.filter(role="CUSTOMER", is_granted=True)
    for rp in customer_perms:
        status = "✅" if rp.permission.code in frontend_codes else "❌"
        print(f"  {status} {rp.permission.code} (granted: {rp.is_granted})")

if __name__ == '__main__':
    analyze_permission_codes()
