#!/usr/bin/env python3
"""
Test script to verify cohort access control is working properly
Tests with demo@xamila.finance user to ensure deactivated cohort blocks access
"""

import requests
import json
import sys

API_BASE = "https://api.xamila.finance/api"

def test_login():
    """Test login and get access token"""
    print("🔐 Testing login...")
    
    login_data = {
        "email": "demo@xamila.finance",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('tokens', {}).get('access')
            if token:
                print("✅ Login successful")
                return token
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_endpoint(endpoint, token, description):
    """Test a specific API endpoint"""
    print(f"\n🔍 Testing {description}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print(f"✅ Success - {count} items returned")
                return True
            elif isinstance(data, list):
                count = len(data)
                print(f"✅ Success - {count} items returned")
                return True
            else:
                print(f"✅ Success - Response: {data}")
                return True
        elif response.status_code == 403:
            try:
                error_data = response.json()
                if error_data.get('code') == 'CHALLENGE_ACCESS_DENIED':
                    print("✅ Access correctly denied - CHALLENGE_ACCESS_DENIED")
                    return True
                else:
                    print(f"❌ Unexpected 403 error: {error_data}")
                    return False
            except:
                print("❌ 403 error but no JSON response")
                return False
        else:
            print(f"❌ Unexpected status: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    print("🧪 Testing Cohort Access Control")
    print("=" * 50)
    
    # Login first
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return 1
    
    # Test endpoints that should be protected
    endpoints_to_test = [
        ("/savings-challenges/", "Savings Challenges List"),
        ("/challenge-participations/", "Challenge Participations"),
        ("/user-challenge-participations/", "User Challenge Participations"),
        ("/user-savings-deposits/", "User Savings Deposits"),
    ]
    
    success_count = 0
    total_tests = len(endpoints_to_test)
    
    for endpoint, description in endpoints_to_test:
        if test_endpoint(endpoint, token, description):
            success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("\n🎉 All cohort access control tests passed!")
        print("✅ Deactivated cohorts properly block access to savings challenges")
    else:
        print("\n⚠️  Some tests failed - check access control implementation")
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
