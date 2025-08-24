#!/usr/bin/env python3
"""
Script de test simple pour l'API KYC CUSTOMER XAMILA
Version sans caracteres Unicode pour compatibilite Windows
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
CUSTOMER_BASE = f"{BASE_URL}/customer"

# Donnees de test
TEST_USER = {
    "email": "test.customer@xamila.com",
    "password": "TestPassword123!",
    "phone": "+33123456789",
    "first_name": "Jean",
    "last_name": "Testeur"
}

def log_message(message, status="INFO"):
    print(f"[{status}] {message}")

def test_server_connection():
    """Test la connexion au serveur Django"""
    log_message("Test connexion serveur Django...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        log_message("Serveur Django accessible", "OK")
        return True
    except requests.exceptions.RequestException as e:
        log_message(f"Serveur Django non accessible: {e}", "ERROR")
        return False

def test_registration():
    """Test inscription client"""
    log_message("Test inscription client...")
    
    try:
        response = requests.post(
            f"{CUSTOMER_BASE}/auth/register/",
            json=TEST_USER,
            timeout=10
        )
        
        log_message(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            user_id = result.get('user_id')
            log_message(f"Inscription reussie - User ID: {user_id}", "SUCCESS")
            return user_id
        else:
            log_message(f"Echec inscription: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_message(f"Erreur inscription: {e}", "ERROR")
        return None

def test_otp_verification(user_id):
    """Test verification OTP (mode mock)"""
    log_message("Test verification OTP...")
    
    if not user_id:
        log_message("User ID manquant", "ERROR")
        return None
    
    # Codes OTP mock pour les tests
    otp_data = {
        "user_id": user_id,
        "email_otp": "123456",
        "sms_otp": "789012"
    }
    
    try:
        response = requests.post(
            f"{CUSTOMER_BASE}/auth/verify-otp/",
            json=otp_data,
            timeout=10
        )
        
        log_message(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get('access_token')
            log_message("Verification OTP reussie", "SUCCESS")
            return access_token
        else:
            log_message(f"Echec verification OTP: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log_message(f"Erreur verification OTP: {e}", "ERROR")
        return None

def test_kyc_profile_creation(access_token):
    """Test creation profil KYC"""
    log_message("Test creation profil KYC...")
    
    if not access_token:
        log_message("Token manquant", "ERROR")
        return False
    
    kyc_data = {
        "first_name": "Jean",
        "last_name": "Testeur",
        "date_of_birth": "1990-05-15",
        "place_of_birth": "Paris, France",
        "nationality": "Francaise",
        "gender": "M",
        "address_line_1": "123 Rue de la Paix",
        "city": "Paris",
        "country": "France",
        "identity_document_type": "NATIONAL_ID",
        "identity_document_number": "123456789TEST",
        "occupation": "Ingenieur logiciel"
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{CUSTOMER_BASE}/kyc/profile/create/",
            json=kyc_data,
            headers=headers,
            timeout=10
        )
        
        log_message(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            log_message("Profil KYC cree avec succes", "SUCCESS")
            return True
        else:
            log_message(f"Echec creation profil KYC: {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"Erreur creation profil KYC: {e}", "ERROR")
        return False

def test_kyc_status(access_token):
    """Test recuperation statut KYC"""
    log_message("Test statut KYC...")
    
    if not access_token:
        log_message("Token manquant", "ERROR")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(
            f"{CUSTOMER_BASE}/kyc/status/",
            headers=headers,
            timeout=10
        )
        
        log_message(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            next_steps = result.get('next_steps', [])
            log_message(f"Statut KYC recupere - Prochaines etapes: {len(next_steps)}", "SUCCESS")
            return True
        else:
            log_message(f"Echec recuperation statut: {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"Erreur statut KYC: {e}", "ERROR")
        return False

def run_basic_tests():
    """Execute les tests de base"""
    print("=" * 60)
    print("TESTS API KYC CUSTOMER XAMILA")
    print("=" * 60)
    
    # Test 1: Connexion serveur
    if not test_server_connection():
        print("ARRET: Serveur non accessible")
        return False
    
    print("-" * 40)
    
    # Test 2: Inscription
    user_id = test_registration()
    if not user_id:
        print("ARRET: Inscription echouee")
        return False
    
    print("-" * 40)
    
    # Test 3: Verification OTP
    access_token = test_otp_verification(user_id)
    if not access_token:
        print("ARRET: Verification OTP echouee")
        return False
    
    print("-" * 40)
    
    # Test 4: Creation profil KYC
    if not test_kyc_profile_creation(access_token):
        print("ARRET: Creation profil KYC echouee")
        return False
    
    print("-" * 40)
    
    # Test 5: Statut KYC
    if not test_kyc_status(access_token):
        print("ARRET: Recuperation statut KYC echouee")
        return False
    
    print("=" * 60)
    print("TOUS LES TESTS DE BASE SONT PASSES!")
    print("L'API KYC CUSTOMER FONCTIONNE CORRECTEMENT")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = run_basic_tests()
    exit(0 if success else 1)
