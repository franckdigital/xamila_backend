#!/usr/bin/env python
"""
Test script to check the live API directly
"""

import requests
import json

def test_live_api():
    """Test the live API endpoints"""
    
    print("=== Testing Live API ===\n")
    
    base_url = "https://api.xamila.finance"
    
    # Test health endpoint first
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   OK Server is reachable")
            health_data = response.json()
            print(f"   Response: {health_data}")
        else:
            print(f"   ERROR Health check failed")
            return
    except requests.exceptions.RequestException as e:
        print(f"   ERROR Connection failed: {e}")
        return
    
    # Test role permissions endpoint (without auth - should get 401)
    print("\n2. Testing role permissions endpoint (no auth)...")
    try:
        response = requests.get(f"{base_url}/api/admin/role-permissions/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print(f"   OK Correctly requires authentication")
        else:
            print(f"   Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   ERROR Request failed: {e}")
    
    # Test with a sample JWT token (if you have one)
    print("\n3. Testing with authentication...")
    print("   Note: You would need a valid JWT token to test this properly")
    print("   The frontend should have detailed console logs when accessing the admin dashboard")
    
    # Instructions for frontend testing
    print("\n=== Frontend Testing Instructions ===")
    print("1. Open the admin dashboard in your browser")
    print("2. Open browser developer tools (F12)")
    print("3. Go to the Console tab")
    print("4. Navigate to the Role Permission Management section")
    print("5. Look for console logs starting with 🔍, 📡, 📊, ✅, or ❌")
    print("6. Check what data is being received from the API")
    
    print("\n=== Expected Console Output ===")
    print("If BASIC role is working correctly, you should see:")
    print("✅ BASIC trouvé dans les données: {permissions...}")
    print("\nIf BASIC role is missing, you should see:")
    print("❌ BASIC NON trouvé dans les données")
    print("Rôles disponibles: ['ADMIN', 'SUPPORT', ...]")

if __name__ == '__main__':
    test_live_api()
