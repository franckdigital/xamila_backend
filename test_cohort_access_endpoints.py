#!/usr/bin/env python3
"""
Test des endpoints d'accès aux cohortes
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "https://api.xamila.finance/api"
TEST_USER_EMAIL = "demo@xamila.finance"
TEST_USER_PASSWORD = "demo123"

def authenticate():
    """Authentification et récupération du token"""
    print("🔐 Authentification...")
    
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login/", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Authentification réussie")
            return token
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Erreur authentification: {str(e)}")
        return None

def test_cohort_access_check(token):
    """Test de vérification d'accès aux cohortes"""
    print("\n🔍 Test vérification accès cohorte...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/user/cohort-access/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint cohort-access fonctionnel")
            print(f"Accès autorisé: {data.get('access_authorized')}")
            print(f"Message: {data.get('message')}")
            print(f"Cohortes utilisateur: {len(data.get('user_cohorts', []))}")
            
            for cohort in data.get('user_cohorts', []):
                print(f"  - {cohort.get('nom')} (actif: {cohort.get('actif')})")
            
            return data.get('access_authorized', False)
        else:
            print(f"❌ Échec endpoint cohort-access: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Erreur test cohort-access: {str(e)}")
        return False

def test_get_user_cohorts(token):
    """Test de récupération des cohortes utilisateur"""
    print("\n📋 Test récupération cohortes utilisateur...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/user/cohorts/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint user/cohorts fonctionnel")
            cohorts = data.get('cohorts', [])
            print(f"Nombre de cohortes: {len(cohorts)}")
            
            for cohort in cohorts:
                print(f"  - ID: {cohort.get('id')}")
                print(f"    Nom: {cohort.get('nom')}")
                print(f"    Actif: {cohort.get('actif')}")
                print(f"    Mois/Année: {cohort.get('mois')}/{cohort.get('annee')}")
            
            return cohorts
        else:
            print(f"❌ Échec endpoint user/cohorts: {response.status_code}")
            print(f"Réponse: {response.text}")
            return []
            
    except Exception as e:
        print(f"💥 Erreur test user/cohorts: {str(e)}")
        return []

def test_join_cohort_invalid_code(token):
    """Test d'adhésion avec un code invalide"""
    print("\n🚫 Test adhésion code invalide...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    join_data = {
        "code_cohorte": "INVALID_CODE_123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/user/join-cohort/", json=join_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            print("✅ Rejet code invalide fonctionnel")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Erreur test code invalide: {str(e)}")
        return False

def test_join_cohort_valid_code(token):
    """Test d'adhésion avec un code valide (si disponible)"""
    print("\n✅ Test adhésion code valide...")
    
    # D'abord, récupérer les cohortes disponibles pour trouver un code valide
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Essayer avec un code cohorte connu (format typique: MOIS-ANNÉE)
    test_codes = ["JAN-2024", "FEV-2024", "MAR-2024", "AVR-2024"]
    
    for code in test_codes:
        print(f"  Test avec code: {code}")
        
        join_data = {
            "code_cohorte": code
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/user/join-cohort/", json=join_data, headers=headers)
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Adhésion réussie avec {code}")
                print(f"  Message: {data.get('message')}")
                return True
            elif response.status_code == 400:
                data = response.json()
                message = data.get('message', '')
                if "déjà membre" in message:
                    print(f"  ℹ️  Déjà membre de {code}")
                    return True
                elif "pas active" in message:
                    print(f"  ⚠️  Cohorte {code} inactive")
                else:
                    print(f"  ❌ Erreur: {message}")
            elif response.status_code == 404:
                print(f"  ❌ Code {code} introuvable")
            else:
                print(f"  ❌ Erreur {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  💥 Erreur test {code}: {str(e)}")
    
    print("  ⚠️  Aucun code valide trouvé dans les tests")
    return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST DES ENDPOINTS D'ACCÈS AUX COHORTES")
    print("=" * 60)
    
    # Authentification
    token = authenticate()
    if not token:
        print("❌ Impossible de continuer sans authentification")
        return False
    
    # Tests des endpoints
    tests = [
        ("Vérification accès cohorte", lambda: test_cohort_access_check(token)),
        ("Récupération cohortes utilisateur", lambda: test_get_user_cohorts(token)),
        ("Adhésion code invalide", lambda: test_join_cohort_invalid_code(token)),
        ("Adhésion code valide", lambda: test_join_cohort_valid_code(token)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"TEST: {test_name}")
        print(f"{'='*40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - SUCCÈS")
            else:
                print(f"❌ {test_name} - ÉCHEC")
                
        except Exception as e:
            print(f"💥 {test_name} - ERREUR: {str(e)}")
            results.append((test_name, False))
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    print(f"\nTests réussis: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
    elif success_count > 0:
        print("⚠️  TESTS PARTIELLEMENT RÉUSSIS")
    else:
        print("❌ TOUS LES TESTS ÉCHOUÉS")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
