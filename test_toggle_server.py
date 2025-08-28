#!/usr/bin/env python3
"""
Script de test pour le serveur de production - à copier sur le serveur
"""
import requests
import json

def test_toggle_status_server():
    """Test l'endpoint toggle-status sur le serveur"""
    
    # Login admin
    login_url = "http://localhost:8000/api/auth/login/"
    admin_data = {
        "email": "xamila.developer@gmail.com",
        "password": "Manager$2025"
    }
    
    try:
        print("=== TEST TOGGLE STATUS ON SERVER ===")
        
        # 1. Login
        response = requests.post(login_url, json=admin_data)
        if response.status_code != 200:
            print(f"[ERROR] Login failed: {response.status_code}")
            return False
            
        login_result = response.json()
        access_token = login_result['tokens']['access']
        user_role = login_result['user']['role']
        
        print(f"[OK] Login successful - Role: {user_role}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 2. Get users list
        users_response = requests.get("http://localhost:8000/api/admin/users/", headers=headers)
        
        if users_response.status_code != 200:
            print(f"[ERROR] Cannot get users: {users_response.status_code}")
            print(users_response.text)
            return False
            
        users_data = users_response.json()
        users = users_data.get('results', [])
        
        print(f"[OK] Found {len(users)} users")
        
        # Check if is_active field is present
        if users:
            first_user = users[0]
            print(f"User fields: {list(first_user.keys())}")
            
            if 'is_active' in first_user:
                print("[SUCCESS] is_active field is present in API response!")
                return True
            else:
                print("[ERROR] is_active field is missing from API response")
                print("Need to add 'is_active' to UserSerializer fields")
                return False
        else:
            print("[ERROR] No users found")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == '__main__':
    test_toggle_status_server()
