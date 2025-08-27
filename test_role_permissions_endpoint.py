#!/usr/bin/env python
"""
Test script for role permissions API endpoint
Tests the /api/admin/role-permissions/ endpoint with proper authentication
"""

import os
import sys
import django
import requests
import json
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from core.models_permissions import Permission, RolePermission

User = get_user_model()

def test_role_permissions_api():
    """Test the role permissions API endpoint"""
    
    print("=== Testing Role Permissions API ===\n")
    
    # Create test client
    client = APIClient()
    
    # Get or create admin user
    try:
        admin_user = User.objects.get(email='admin@xamila.com')
        print(f"✓ Found existing admin user: {admin_user.email}")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            email='admin@xamila.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True
        )
        print(f"✓ Created admin user: {admin_user.email}")
    
    # Generate JWT token
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    print(f"✓ Generated JWT token for admin")
    
    # Set authentication header
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test the role permissions endpoint
    print("\n--- Testing /api/admin/role-permissions/ endpoint ---")
    
    response = client.get('/api/admin/role-permissions/')
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.items())}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ API call successful")
        print(f"Response keys: {list(data.keys())}")
        
        if 'role_permissions' in data:
            role_permissions = data['role_permissions']
            print(f"✓ Found role_permissions in response")
            print(f"Available roles: {list(role_permissions.keys())}")
            
            # Check for BASIC role
            if 'BASIC' in role_permissions:
                print(f"✓ BASIC role found in API response")
                basic_permissions = role_permissions['BASIC']
                print(f"BASIC role permissions: {basic_permissions}")
                
                # Check for bilans_financiers permission
                if 'bilans_financiers' in basic_permissions:
                    print(f"✓ bilans_financiers permission found for BASIC role")
                    print(f"bilans_financiers value: {basic_permissions['bilans_financiers']}")
                else:
                    print(f"✗ bilans_financiers permission NOT found for BASIC role")
                    print(f"Available permissions for BASIC: {list(basic_permissions.keys())}")
            else:
                print(f"✗ BASIC role NOT found in API response")
                print(f"Available roles: {list(role_permissions.keys())}")
        else:
            print(f"✗ role_permissions key not found in response")
            print(f"Response data: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ API call failed with status {response.status_code}")
        print(f"Response content: {response.content.decode()}")
    
    # Check database state
    print("\n--- Checking Database State ---")
    
    # Check permissions
    permissions = Permission.objects.all()
    print(f"Total permissions in database: {permissions.count()}")
    
    bilans_perm = Permission.objects.filter(code='bilans_financiers').first()
    if bilans_perm:
        print(f"✓ bilans_financiers permission exists: {bilans_perm.name}")
    else:
        print(f"✗ bilans_financiers permission not found")
    
    # Check role permissions
    role_perms = RolePermission.objects.all()
    print(f"Total role permissions in database: {role_perms.count()}")
    
    basic_role_perms = RolePermission.objects.filter(role='BASIC')
    print(f"BASIC role permissions count: {basic_role_perms.count()}")
    
    if basic_role_perms.exists():
        print("BASIC role permissions:")
        for rp in basic_role_perms:
            print(f"  - {rp.permission.code}: {rp.is_granted}")
    
    # Check specific bilans_financiers for BASIC
    basic_bilans = RolePermission.objects.filter(
        role='BASIC',
        permission__code='bilans_financiers'
    ).first()
    
    if basic_bilans:
        print(f"✓ BASIC role has bilans_financiers permission: {basic_bilans.is_granted}")
    else:
        print(f"✗ BASIC role does not have bilans_financiers permission")

def test_with_requests():
    """Test using requests library against live server"""
    
    print("\n=== Testing with Requests Library ===\n")
    
    # Test against live server
    base_url = "https://api.xamila.finance"
    
    # Try to get a token first (you would need valid credentials)
    print(f"Testing against: {base_url}")
    
    # For now, just test if the server is reachable
    try:
        response = requests.get(f"{base_url}/health/", timeout=10)
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Server is reachable")
            print(f"Health response: {response.json()}")
        else:
            print(f"✗ Server returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Server connection failed: {e}")

if __name__ == '__main__':
    test_role_permissions_api()
    test_with_requests()
