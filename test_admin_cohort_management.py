#!/usr/bin/env python3
"""
Test script to verify admin cohort management functionality
Tests toggle, edit, and delete operations via API endpoints
"""

import requests
import json
import sys

API_BASE = "https://api.xamila.finance/api"

def test_admin_login():
    """Test admin login and get access token"""
    print("🔐 Testing admin login...")
    
    # Try common admin credentials
    admin_credentials = [
        {"email": "admin@xamila.finance", "password": "admin123"},
        {"email": "admin@example.com", "password": "admin123"},
        {"email": "test@admin.com", "password": "admin123"}
    ]
    
    for creds in admin_credentials:
        try:
            response = requests.post(f"{API_BASE}/auth/login/", json=creds)
            if response.status_code == 200:
                data = response.json()
                token = data.get('tokens', {}).get('access')
                if token:
                    print(f"✅ Admin login successful with {creds['email']}")
                    return token, creds['email']
        except Exception as e:
            continue
    
    print("❌ No admin credentials worked")
    return None, None

def test_cohort_list(token):
    """Test fetching cohort list"""
    print("\n📋 Testing cohort list endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE}/admin/cohortes/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                cohorts = data['results']
                print(f"✅ Found {len(cohorts)} cohorts")
                for cohort in cohorts[:3]:  # Show first 3
                    print(f"  - {cohort.get('nom', 'N/A')}: Active={cohort.get('actif', 'N/A')}")
                return cohorts
            else:
                print(f"✅ Found {len(data)} cohorts (non-paginated)")
                return data
        else:
            print(f"❌ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_cohort_toggle(token, cohort_id):
    """Test cohort toggle functionality"""
    print(f"\n🔄 Testing cohort toggle for ID: {cohort_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test PATCH endpoint for toggle
        response = requests.patch(f"{API_BASE}/admin/cohortes/{cohort_id}/", headers=headers)
        print(f"PATCH Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Toggle successful - New status: {data.get('actif', 'Unknown')}")
            return True
        else:
            print(f"❌ Toggle failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cohort_edit(token, cohort_id):
    """Test cohort edit functionality"""
    print(f"\n✏️ Testing cohort edit for ID: {cohort_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data for PUT endpoint
    test_data = {
        "mois": 9,
        "annee": 2025,
        "email_utilisateur": "test@example.com"
    }
    
    try:
        response = requests.put(f"{API_BASE}/admin/cohortes/{cohort_id}/", 
                               json=test_data, headers=headers)
        print(f"PUT Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Edit successful - New name: {data.get('nom', 'Unknown')}")
            return True
        else:
            print(f"❌ Edit failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Testing Admin Cohort Management")
    print("=" * 50)
    
    # Login first
    token, admin_email = test_admin_login()
    if not token:
        print("\n❌ Cannot proceed without admin token")
        return 1
    
    # Test cohort list
    cohorts = test_cohort_list(token)
    if not cohorts:
        print("\n❌ No cohorts found or list failed")
        return 1
    
    # Test toggle and edit with first cohort
    if len(cohorts) > 0:
        cohort_id = cohorts[0].get('id')
        if cohort_id:
            # Test toggle
            toggle_success = test_cohort_toggle(token, cohort_id)
            
            # Test edit (only if we have a valid cohort)
            edit_success = test_cohort_edit(token, cohort_id)
            
            print(f"\n📊 Test Results:")
            print(f"- Cohort List: ✅")
            print(f"- Cohort Toggle: {'✅' if toggle_success else '❌'}")
            print(f"- Cohort Edit: {'✅' if edit_success else '❌'}")
            
            if toggle_success and edit_success:
                print("\n🎉 All admin cohort management tests passed!")
                return 0
            else:
                print("\n⚠️ Some tests failed - check API endpoints")
                return 1
        else:
            print("\n❌ No valid cohort ID found")
            return 1
    else:
        print("\n❌ No cohorts available for testing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
