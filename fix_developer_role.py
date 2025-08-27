#!/usr/bin/env python3
"""
Django management script to fix xamila.developer@gmail.com role
Run this on the production server where the database is accessible
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User

def fix_developer_role():
    """Fix xamila.developer@gmail.com role to BASIC"""
    try:
        # Try to find existing user
        user = User.objects.get(email='xamila.developer@gmail.com')
        print(f"Found user: {user.email}")
        print(f"Current role: {user.role}")
        print(f"User ID: {user.id}")
        
        if user.role == 'CUSTOMER':
            print("PROBLEM: User has CUSTOMER role, should be BASIC")
            user.role = 'BASIC'
            user.save()
            print("FIXED: Updated role to BASIC")
            print("User will now redirect to /dashboard/bilans-financiers")
        else:
            print(f"User role is already {user.role}")
            
        return user
        
    except User.DoesNotExist:
        print("User xamila.developer@gmail.com not found")
        print("Creating new BASIC user for testing...")
        
        # Create new user with BASIC role
        user = User.objects.create_user(
            email='xamila.developer@gmail.com',
            password='developer123',
            role='BASIC',
            first_name='Developer',
            last_name='Test',
            is_verified=True,
            is_active=True
        )
        print(f"Created new BASIC user: {user.email}")
        print(f"Password: developer123")
        return user
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    print("Fixing xamila.developer@gmail.com role to BASIC...")
    user = fix_developer_role()
    
    if user:
        print(f"\nSUCCESS!")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Login and test redirection to /dashboard/bilans-financiers")
    else:
        print("\nFAILED to fix user role")
