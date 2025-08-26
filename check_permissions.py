#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def check_permissions():
    print("=== VÉRIFICATION DES PERMISSIONS ===\n")
    
    # Vérifier toutes les permissions
    print("1. PERMISSIONS DISPONIBLES:")
    permissions = Permission.objects.all()
    for perm in permissions:
        print(f"   - {perm.code}: {perm.name}")
    
    print(f"\nTotal permissions: {permissions.count()}\n")
    
    # Vérifier les permissions du rôle CUSTOMER
    print("2. PERMISSIONS RÔLE CUSTOMER:")
    customer_perms = RolePermission.objects.filter(role='CUSTOMER')
    
    if not customer_perms.exists():
        print("   ❌ AUCUNE permission trouvée pour CUSTOMER!")
        return
    
    for rp in customer_perms:
        status = "✅ ACCORDÉE" if rp.is_granted else "❌ REFUSÉE"
        active = "ACTIVE" if rp.is_active else "INACTIVE"
        print(f"   - {rp.permission.code}: {status} ({active})")
    
    print(f"\nTotal permissions CUSTOMER: {customer_perms.count()}")
    
    # Compter les permissions accordées
    granted_count = customer_perms.filter(is_granted=True).count()
    print(f"Permissions accordées: {granted_count}")
    
    if granted_count == 0:
        print("\n⚠️  PROBLÈME: Aucune permission accordée pour CUSTOMER!")
        print("   Vérifiez l'admin Django et cochez 'Is granted' pour les permissions nécessaires.")

if __name__ == "__main__":
    check_permissions()
