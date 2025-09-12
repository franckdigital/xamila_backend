#!/usr/bin/env python3
"""
Server restart commands and monitoring for Xamila production deployment
"""

import requests
import time
import subprocess
import sys

def test_server_status():
    """Test if server is responding"""
    try:
        response = requests.get("https://api.xamila.finance/health/", timeout=10)
        return response.status_code == 200
    except:
        return False

def wait_for_server_restart(max_wait=300):
    """Wait for server to come back online after restart"""
    print("Waiting for server to restart...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if test_server_status():
            print(f"✓ Server is back online after {int(time.time() - start_time)} seconds")
            return True
        
        print(".", end="", flush=True)
        time.sleep(10)
    
    print(f"\n✗ Server did not come back online within {max_wait} seconds")
    return False

def test_api_endpoints():
    """Test critical API endpoints after restart"""
    print("\nTesting API endpoints...")
    
    endpoints = [
        ("Health Check", "GET", "https://api.xamila.finance/health/"),
        ("Auth Login", "POST", "https://api.xamila.finance/api/auth/login/"),
        ("Admin Cohortes", "GET", "https://api.xamila.finance/api/admin/cohortes/"),
    ]
    
    for name, method, url in endpoints:
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                # For POST, just test if endpoint exists (will return 400 without data)
                response = requests.post(url, json={}, timeout=10)
            
            if response.status_code in [200, 400, 401]:  # 400/401 means endpoint exists
                print(f"✓ {name}: {response.status_code}")
            else:
                print(f"✗ {name}: {response.status_code}")
                
        except Exception as e:
            print(f"✗ {name}: Error - {e}")

def test_cors_functionality():
    """Test CORS headers after restart"""
    print("\nTesting CORS functionality...")
    
    try:
        headers = {
            'Origin': 'https://xamila.finance',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options("https://api.xamila.finance/api/auth/login/", 
                                  headers=headers, timeout=10)
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_origin:
            print(f"✓ CORS headers present: {cors_origin}")
        else:
            print("✗ CORS headers missing")
            
    except Exception as e:
        print(f"✗ CORS test failed: {e}")

def main():
    print("Xamila Server Restart Monitoring")
    print("=" * 50)
    
    # Check current status
    print("Checking current server status...")
    if test_server_status():
        print("✓ Server is currently online")
    else:
        print("✗ Server is currently offline (502 errors)")
    
    print("\nServer restart commands (run on production server):")
    print("-" * 50)
    print("# Pull latest code:")
    print("cd /path/to/xamila_backend && git pull origin master")
    print()
    print("# Restart Django (choose appropriate method):")
    print("sudo systemctl restart xamila-backend")
    print("# OR")
    print("sudo supervisorctl restart xamila-backend") 
    print("# OR")
    print("pkill -f 'python manage.py runserver' && python manage.py runserver 0.0.0.0:8000 &")
    print()
    print("# Restart web server:")
    print("sudo systemctl restart nginx")
    print()
    
    # Wait for user to restart server
    input("Press Enter after restarting the server to begin monitoring...")
    
    # Monitor restart
    if wait_for_server_restart():
        test_api_endpoints()
        test_cors_functionality()
        
        print("\n" + "=" * 50)
        print("POST-RESTART VERIFICATION:")
        print("✓ Run cohort management tests")
        print("✓ Test admin dashboard functionality") 
        print("✓ Verify certificate logic")
        print("✓ Deploy frontend build")
    else:
        print("\n" + "=" * 50)
        print("SERVER RESTART FAILED")
        print("Check server logs for errors:")
        print("- Django application logs")
        print("- Nginx error logs: /var/log/nginx/error.log")
        print("- System logs: journalctl -u xamila-backend")

if __name__ == "__main__":
    main()
