#!/usr/bin/env python3
"""
Vérification simple des endpoints d'accès aux cohortes
"""

import requests

def check_endpoint_exists(url):
    """Vérifie si un endpoint existe (sans authentification)"""
    try:
        response = requests.get(url)
        # 401 = endpoint existe mais nécessite authentification
        # 404 = endpoint n'existe pas
        return response.status_code != 404
    except:
        return False

def main():
    base_url = "https://api.xamila.finance/api"
    
    endpoints = [
        "/user/cohort-access/",
        "/user/join-cohort/", 
        "/user/cohorts/"
    ]
    
    print("🔍 Vérification des endpoints cohort access...")
    
    for endpoint in endpoints:
        url = base_url + endpoint
        exists = check_endpoint_exists(url)
        status = "✅ Existe" if exists else "❌ Manquant"
        print(f"{endpoint}: {status}")
    
    return all(check_endpoint_exists(base_url + ep) for ep in endpoints)

if __name__ == "__main__":
    main()
