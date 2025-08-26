#!/usr/bin/env python
"""
Script pour corriger les permissions is_staff et is_superuser de l'admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_admin_permissions():
    """
    Corrige les permissions is_staff et is_superuser de l'admin
    """
    admin_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    print("🔧 CORRECTION PERMISSIONS ADMIN")
    print("=" * 50)
    
    try:
        admin = User.objects.get(id=admin_id)
        print(f"📋 État actuel:")
        print(f"   is_staff: {admin.is_staff}")
        print(f"   is_superuser: {admin.is_superuser}")
        print(f"   is_active: {admin.is_active}")
        print(f"   role: {admin.role}")
        
        # Corriger les permissions
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        
        print(f"\n✅ Permissions corrigées:")
        print(f"   is_staff: {admin.is_staff}")
        print(f"   is_superuser: {admin.is_superuser}")
        print(f"   is_active: {admin.is_active}")
        
        return admin
        
    except User.DoesNotExist:
        print(f"❌ Admin non trouvé avec l'ID: {admin_id}")
        return None

if __name__ == '__main__':
    fix_admin_permissions()
    print("\n" + "=" * 50)
    print("✅ Admin configuré correctement")
    print("   Les switches de permissions devraient maintenant fonctionner")
    print("=" * 50)
