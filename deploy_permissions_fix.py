#!/usr/bin/env python
"""
Deployment script to fix BASIC role and permissions on production server
This script should be run on the production server where the database is accessible
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models_permissions import Permission, RolePermission

def deploy_permissions_fix():
    """Deploy the permissions fix to production"""
    
    print("=== Deploying BASIC Role and Permissions Fix ===\n")
    
    # Step 1: Ensure bilans_financiers permission exists
    print("1. Creating/updating bilans_financiers permission...")
    
    bilans_perm, created = Permission.objects.get_or_create(
        code='bilans_financiers',
        defaults={
            'name': 'Bilans Financiers',
            'category': 'Services Financiers',
            'description': 'Accès aux bilans financiers et rapports'
        }
    )
    
    if created:
        print(f"   ✓ Created bilans_financiers permission")
    else:
        print(f"   ✓ bilans_financiers permission already exists")
    
    # Step 2: Ensure BASIC role has bilans_financiers permission
    print("\n2. Assigning bilans_financiers to BASIC role...")
    
    basic_bilans, created = RolePermission.objects.get_or_create(
        role='BASIC',
        permission=bilans_perm,
        defaults={'is_granted': True}
    )
    
    if created:
        print(f"   ✓ Assigned bilans_financiers to BASIC role")
    else:
        if not basic_bilans.is_granted:
            basic_bilans.is_granted = True
            basic_bilans.save()
            print(f"   ✓ Enabled bilans_financiers for BASIC role")
        else:
            print(f"   ✓ BASIC role already has bilans_financiers permission")
    
    # Step 3: Verify the fix
    print("\n3. Verifying the fix...")
    
    # Check all permissions
    all_permissions = Permission.objects.all().count()
    print(f"   Total permissions in database: {all_permissions}")
    
    # Check BASIC role permissions
    basic_permissions = RolePermission.objects.filter(role='BASIC', is_granted=True)
    print(f"   BASIC role permissions count: {basic_permissions.count()}")
    
    if basic_permissions.exists():
        print("   BASIC role permissions:")
        for rp in basic_permissions:
            print(f"     - {rp.permission.code}: {rp.permission.name}")
    
    # Check specific bilans_financiers for BASIC
    basic_bilans_check = RolePermission.objects.filter(
        role='BASIC',
        permission__code='bilans_financiers',
        is_granted=True
    ).exists()
    
    if basic_bilans_check:
        print(f"   ✓ BASIC role has bilans_financiers permission (GRANTED)")
    else:
        print(f"   ✗ BASIC role missing bilans_financiers permission")
    
    # Step 4: Test API response structure
    print("\n4. Testing API response structure...")
    
    try:
        # Simulate the API response
        role_permissions_data = {}
        roles = RolePermission.objects.values_list('role', flat=True).distinct().order_by('role')
        
        for role in roles:
            role_permissions_data[role] = {}
            role_perms = RolePermission.objects.filter(role=role).select_related('permission')
            for rp in role_perms:
                role_permissions_data[role][rp.permission.code] = rp.is_granted
        
        print(f"   Available roles in API response: {list(role_permissions_data.keys())}")
        
        if 'BASIC' in role_permissions_data:
            basic_perms = role_permissions_data['BASIC']
            print(f"   ✓ BASIC role found in API response")
            print(f"   BASIC permissions: {list(basic_perms.keys())}")
            
            if 'bilans_financiers' in basic_perms:
                print(f"   ✓ bilans_financiers found for BASIC: {basic_perms['bilans_financiers']}")
            else:
                print(f"   ✗ bilans_financiers NOT found for BASIC")
        else:
            print(f"   ✗ BASIC role NOT found in API response")
            
    except Exception as e:
        print(f"   ✗ Error testing API structure: {e}")
    
    print("\n=== Deployment Complete ===")
    print("The BASIC role and bilans_financiers permission should now be properly configured.")
    print("Test the admin dashboard to verify the fix is working.")

if __name__ == '__main__':
    deploy_permissions_fix()
