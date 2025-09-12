#!/usr/bin/env python3
"""
Simple server status check for Xamila API
"""

import requests
import socket
import time

def check_dns_resolution():
    """Check if DNS resolves correctly"""
    print("1. DNS Resolution Check")
    print("-" * 30)
    
    try:
        ip = socket.gethostbyname('api.xamila.finance')
        print(f"OK api.xamila.finance resolves to: {ip}")
        return True
    except socket.gaierror as e:
        print(f"ERROR DNS resolution failed: {e}")
        return False

def check_http_endpoints():
    """Check various HTTP endpoints"""
    print("\n2. HTTP Endpoints Check")
    print("-" * 30)
    
    endpoints = [
        "https://api.xamila.finance/",
        "https://api.xamila.finance/health/",
        "https://api.xamila.finance/api/",
        "https://api.xamila.finance/api/auth/login/",
    ]
    
    for url in endpoints:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"  Response: {str(data)[:100]}...")
                    except:
                        print(f"  Response: {response.text[:100]}...")
                else:
                    print(f"  Content-Type: {content_type}")
                    print(f"  Response: {response.text[:100]}...")
            elif response.status_code == 502:
                print("  ERROR 502 Bad Gateway - Server is down or misconfigured")
            elif response.status_code == 503:
                print("  ERROR 503 Service Unavailable - Server temporarily unavailable")
            elif response.status_code == 404:
                print("  ERROR 404 Not Found - Endpoint doesn't exist")
            else:
                print(f"  Response: {response.text[:100]}...")
                
        except requests.exceptions.ConnectTimeout:
            print("  ERROR Connection timeout")
        except requests.exceptions.ConnectionError as e:
            print(f"  ERROR Connection error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"  ERROR Request error: {e}")

def test_cors_simple():
    """Simple CORS test"""
    print("\n3. CORS Test")
    print("-" * 30)
    
    try:
        headers = {
            'Origin': 'https://xamila.finance',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options("https://api.xamila.finance/api/auth/login/", headers=headers, timeout=10)
        print(f"OPTIONS request status: {response.status_code}")
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        print(f"Access-Control-Allow-Origin: {cors_origin}")
        
        if cors_origin:
            print("OK CORS headers present")
        else:
            print("ERROR No CORS headers")
            
    except Exception as e:
        print(f"ERROR CORS test failed: {e}")

def main():
    print("Xamila API Server Status Check")
    print("=" * 50)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run checks
    dns_ok = check_dns_resolution()
    
    if dns_ok:
        check_http_endpoints()
        test_cors_simple()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("- 502 errors mean the Django server is down")
    print("- Server needs to be restarted to apply code changes")
    print("- Check server logs for specific error details")

if __name__ == "__main__":
    main()
