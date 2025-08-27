#!/usr/bin/env python
"""
Test script to verify the API structure being returned
"""

import requests
import json

def test_api_structure():
    """Test the actual API structure being returned"""
    
    print("=== Testing API Structure ===\n")
    
    base_url = "https://api.xamila.finance"
    
    # Test the role permissions endpoint structure
    print("Testing /api/admin/role-permissions/ endpoint structure...")
    
    # Note: This will fail without authentication, but we can see the endpoint structure
    try:
        response = requests.get(f"{base_url}/api/admin/role-permissions/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Endpoint exists (requires authentication)")
        elif response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list):
                print(f"✗ API returning array of {len(data)} items (incorrect format)")
                if data:
                    print(f"Sample item: {data[0]}")
            elif isinstance(data, dict) and 'role_permissions' in data:
                print(f"✓ API returning correct nested structure")
                print(f"Roles found: {list(data['role_permissions'].keys())}")
            else:
                print(f"✗ API returning unexpected format: {data}")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    
    print("\n=== Expected vs Actual Structure ===")
    print("Expected structure:")
    print(json.dumps({
        "role_permissions": {
            "BASIC": {"bilans_financiers": True},
            "ADMIN": {"admin_dashboard": True, "bilans_financiers": True}
        }
    }, indent=2))
    
    print("\nActual structure (from console logs):")
    print("Array of 95 objects like:")
    print(json.dumps([
        {
            "id": 1,
            "role": "CUSTOMER", 
            "permission": {"code": "dashboard.view", "name": "Dashboard View"},
            "is_granted": True
        }
    ], indent=2))

if __name__ == '__main__':
    test_api_structure()
