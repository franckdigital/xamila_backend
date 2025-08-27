#!/usr/bin/env python
"""
Test script to authenticate and check role permissions API
"""

import requests
import json

def test_authenticated_api():
    """Test the API with authentication"""
    
    print("=== Testing Authenticated API ===\n")
    
    base_url = "https://api.xamila.finance"
    
    # Step 1: Try to authenticate with admin credentials
    print("1. Attempting admin authentication...")
    
    login_data = {
        "email": "admin@xamila.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/admin/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data.get('access')
            print(f"   OK Authentication successful")
            print(f"   Token received: {access_token[:50]}..." if access_token else "No token")
            
            if access_token:
                # Step 2: Test role permissions endpoint with token
                print("\n2. Testing role permissions with authentication...")
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    f"{base_url}/api/admin/role-permissions/",
                    headers=headers,
                    timeout=10
                )
                
                print(f"   Role Permissions Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   OK Role permissions retrieved successfully")
                    
                    # Check the data structure
                    if 'role_permissions' in data:
                        role_permissions = data['role_permissions']
                        available_roles = list(role_permissions.keys())
                        print(f"   Available roles: {available_roles}")
                        
                        # Check for BASIC role specifically
                        if 'BASIC' in role_permissions:
                            print(f"   OK BASIC role found in API response")
                            basic_perms = role_permissions['BASIC']
                            print(f"   BASIC permissions: {list(basic_perms.keys())}")
                            
                            # Check for bilans_financiers permission
                            if 'bilans_financiers' in basic_perms:
                                print(f"   OK bilans_financiers found for BASIC role")
                                print(f"   Value: {basic_perms['bilans_financiers']}")
                            else:
                                print(f"   ERROR bilans_financiers NOT found for BASIC role")
                        else:
                            print(f"   ERROR BASIC role NOT found in API response")
                            print(f"   This explains why the frontend doesn't show BASIC role")
                    else:
                        print(f"   ERROR role_permissions key not found in response")
                        print(f"   Response keys: {list(data.keys())}")
                else:
                    error_text = response.text
                    print(f"   ERROR Role permissions request failed: {error_text[:200]}")
            else:
                print("   ERROR No access token received")
        else:
            error_text = response.text
            print(f"   ERROR Authentication failed: {error_text[:200]}")
            
            # Try alternative login endpoints
            print("\n   Trying alternative admin login endpoint...")
            try:
                response = requests.post(
                    f"{base_url}/api/auth/login/",
                    json=login_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                print(f"   Alternative login status: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Alternative login failed: {response.text[:200]}")
            except Exception as e:
                print(f"   Alternative login error: {e}")
                
    except requests.exceptions.RequestException as e:
        print(f"   ERROR Connection failed: {e}")
    
    # Step 3: Instructions for manual testing
    print("\n=== Manual Testing Instructions ===")
    print("If authentication failed, you can manually test by:")
    print("1. Open the admin dashboard at https://xamila.finance/admin")
    print("2. Login with admin credentials")
    print("3. Open browser developer tools (F12)")
    print("4. Go to Console tab")
    print("5. Navigate to Role Permission Management")
    print("6. Look for console logs to see what data is received")
    print("7. Check Network tab to see the actual API requests and responses")
    
    print("\n=== Expected Frontend Behavior ===")
    print("The frontend RolePermissionManagement.js component should log:")
    print("- Token presence/absence")
    print("- API response status")
    print("- Received data structure")
    print("- Whether BASIC role is found in the data")
    print("- Available roles if BASIC is missing")

if __name__ == '__main__':
    test_authenticated_api()
