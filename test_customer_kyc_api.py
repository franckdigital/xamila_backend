#!/usr/bin/env python3
"""
Script de test complet pour l'API KYC CUSTOMER XAMILA
Teste tous les endpoints d'inscription, connexion, KYC et upload de documents
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
CUSTOMER_BASE = f"{BASE_URL}/customer"

# Données de test
TEST_USER = {
    "email": "test.customer@xamila.com",
    "password": "TestPassword123!",
    "phone": "+33123456789",
    "first_name": "Jean",
    "last_name": "Testeur"
}

TEST_KYC_PROFILE = {
    "first_name": "Jean",
    "last_name": "Testeur",
    "middle_name": "Pierre",
    "date_of_birth": "1990-05-15",
    "place_of_birth": "Paris, France",
    "nationality": "Française",
    "gender": "M",
    "address_line_1": "123 Rue de la Paix",
    "address_line_2": "Appartement 4B",
    "city": "Paris",
    "state_province": "Île-de-France",
    "postal_code": "75001",
    "country": "France",
    "identity_document_type": "NATIONAL_ID",
    "identity_document_number": "123456789TEST",
    "identity_document_expiry": "2030-05-15",
    "identity_document_issuing_country": "France",
    "occupation": "Ingénieur logiciel",
    "employer_name": "Tech Corp",
    "monthly_income": 4500.00,
    "source_of_funds": "SALARY"
}

class XamilaAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.kyc_profile_id = None
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
    
    def test_endpoint(self, method, endpoint, data=None, files=None, auth=True):
        """Test un endpoint et affiche le résultat"""
        url = f"{CUSTOMER_BASE}{endpoint}"
        
        headers = {}
        if auth and self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        self.log(f"Testing {method} {endpoint}")
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = self.session.post(url, json=data, headers=headers)
            elif method == "PUT":
                headers['Content-Type'] = 'application/json'
                response = self.session.put(url, json=data, headers=headers)
            
            self.log(f"Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                self.log(f"Response: {json.dumps(result, indent=2)}")
                return response.status_code, result
            else:
                self.log(f"Response: {response.text[:200]}...")
                return response.status_code, response.text
                
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            return None, str(e)
    
    def test_registration(self):
        """Test l'inscription d'un nouveau client"""
        self.log("=== TEST INSCRIPTION CLIENT ===", "TEST")
        
        status, result = self.test_endpoint("POST", "/auth/register/", TEST_USER, auth=False)
        
        if status == 201:
            self.user_id = result.get('user_id')
            self.log(f"[OK] Inscription réussie - User ID: {self.user_id}", "SUCCESS")
            return True
        else:
            self.log("[ERREUR] Echec de l'inscription", "ERROR")
            return False
    
    def test_otp_verification(self):
        """Test la vérification OTP (mode mock)"""
        self.log("=== TEST VÉRIFICATION OTP ===", "TEST")
        
        if not self.user_id:
            self.log("❌ User ID manquant", "ERROR")
            return False
        
        # En mode mock, utiliser des codes OTP prédéfinis
        otp_data = {
            "user_id": self.user_id,
            "email_otp": "123456",  # Code mock
            "sms_otp": "789012"     # Code mock
        }
        
        status, result = self.test_endpoint("POST", "/auth/verify-otp/", otp_data, auth=False)
        
        if status == 200:
            self.access_token = result.get('access_token')
            self.log(f"✅ Vérification OTP réussie - Token reçu", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la vérification OTP", "ERROR")
            return False
    
    def test_login(self):
        """Test la connexion client"""
        self.log("=== TEST CONNEXION CLIENT ===", "TEST")
        
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        status, result = self.test_endpoint("POST", "/auth/login/", login_data, auth=False)
        
        if status == 200:
            self.access_token = result.get('access_token')
            self.log(f"✅ Connexion réussie", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la connexion", "ERROR")
            return False
    
    def test_kyc_profile_creation(self):
        """Test la création du profil KYC"""
        self.log("=== TEST CRÉATION PROFIL KYC ===", "TEST")
        
        status, result = self.test_endpoint("POST", "/kyc/profile/create/", TEST_KYC_PROFILE)
        
        if status == 201:
            self.kyc_profile_id = result.get('id')
            self.log(f"✅ Profil KYC créé - ID: {self.kyc_profile_id}", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la création du profil KYC", "ERROR")
            return False
    
    def test_kyc_profile_retrieval(self):
        """Test la récupération du profil KYC"""
        self.log("=== TEST RÉCUPÉRATION PROFIL KYC ===", "TEST")
        
        status, result = self.test_endpoint("GET", "/kyc/profile/")
        
        if status == 200:
            completion = result.get('completion_percentage', 0)
            kyc_status = result.get('kyc_status', 'UNKNOWN')
            self.log(f"✅ Profil récupéré - Statut: {kyc_status}, Completion: {completion}%", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la récupération du profil", "ERROR")
            return False
    
    def test_kyc_status(self):
        """Test la récupération du statut KYC détaillé"""
        self.log("=== TEST STATUT KYC DÉTAILLÉ ===", "TEST")
        
        status, result = self.test_endpoint("GET", "/kyc/status/")
        
        if status == 200:
            next_steps = result.get('next_steps', [])
            required_docs = result.get('required_documents', [])
            self.log(f"✅ Statut récupéré - Prochaines étapes: {len(next_steps)}, Documents requis: {len(required_docs)}", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la récupération du statut", "ERROR")
            return False
    
    def create_test_image(self, filename="test_document.jpg"):
        """Crée une image de test pour l'upload"""
        try:
            from PIL import Image
            import io
            
            # Créer une image simple
            img = Image.new('RGB', (300, 200), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            return img_bytes
        except ImportError:
            # Fallback: créer un fichier texte simple
            content = b"FAKE_IMAGE_DATA_FOR_TESTING_PURPOSES_ONLY"
            return io.BytesIO(content)
    
    def test_document_upload(self):
        """Test l'upload de documents KYC"""
        self.log("=== TEST UPLOAD DOCUMENTS KYC ===", "TEST")
        
        documents_to_test = [
            ("IDENTITY_FRONT", "carte_identite_recto.jpg"),
            ("SELFIE", "selfie.jpg"),
            ("PROOF_OF_ADDRESS", "justificatif_domicile.jpg")
        ]
        
        success_count = 0
        
        for doc_type, filename in documents_to_test:
            self.log(f"Upload document: {doc_type}")
            
            # Créer un fichier de test
            test_file = self.create_test_image(filename)
            
            data = {"document_type": doc_type}
            files = {"file": (filename, test_file, "image/jpeg")}
            
            status, result = self.test_endpoint("POST", "/kyc/documents/upload/", data, files)
            
            if status == 201:
                self.log(f"✅ Document {doc_type} uploadé avec succès", "SUCCESS")
                success_count += 1
            else:
                self.log(f"❌ Échec upload document {doc_type}", "ERROR")
        
        return success_count == len(documents_to_test)
    
    def test_documents_list(self):
        """Test la récupération de la liste des documents"""
        self.log("=== TEST LISTE DOCUMENTS ===", "TEST")
        
        status, result = self.test_endpoint("GET", "/kyc/documents/")
        
        if status == 200:
            doc_count = len(result) if isinstance(result, list) else 0
            self.log(f"✅ Liste récupérée - {doc_count} documents", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la récupération de la liste", "ERROR")
            return False
    
    def test_kyc_submission(self):
        """Test la soumission du profil KYC pour révision"""
        self.log("=== TEST SOUMISSION KYC ===", "TEST")
        
        status, result = self.test_endpoint("POST", "/kyc/submit/", {})
        
        if status == 200:
            new_status = result.get('status', 'UNKNOWN')
            self.log(f"✅ Profil soumis avec succès - Nouveau statut: {new_status}", "SUCCESS")
            return True
        else:
            self.log("❌ Échec de la soumission", "ERROR")
            return False
    
    def test_resend_otp(self):
        """Test le renvoi d'OTP"""
        self.log("=== TEST RENVOI OTP ===", "TEST")
        
        if not self.user_id:
            self.log("❌ User ID manquant", "ERROR")
            return False
        
        otp_data = {
            "user_id": self.user_id,
            "otp_type": "email"
        }
        
        status, result = self.test_endpoint("POST", "/auth/resend-otp/", otp_data, auth=False)
        
        if status == 200:
            self.log("✅ OTP renvoyé avec succès", "SUCCESS")
            return True
        else:
            self.log("❌ Échec du renvoi OTP", "ERROR")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests dans l'ordre"""
        self.log("DEBUT DES TESTS API KYC CUSTOMER XAMILA", "START")
        
        tests = [
            ("Inscription", self.test_registration),
            ("Vérification OTP", self.test_otp_verification),
            ("Connexion", self.test_login),
            ("Création profil KYC", self.test_kyc_profile_creation),
            ("Récupération profil KYC", self.test_kyc_profile_retrieval),
            ("Statut KYC détaillé", self.test_kyc_status),
            ("Upload documents", self.test_document_upload),
            ("Liste documents", self.test_documents_list),
            ("Soumission KYC", self.test_kyc_submission),
            ("Renvoi OTP", self.test_resend_otp),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*50}")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    self.log(f"✅ {test_name}: SUCCÈS", "PASS")
                else:
                    self.log(f"❌ {test_name}: ÉCHEC", "FAIL")
            except Exception as e:
                self.log(f"💥 {test_name}: ERREUR - {str(e)}", "ERROR")
                results.append((test_name, False))
            
            time.sleep(1)  # Pause entre les tests
        
        # Résumé final
        self.log(f"\n{'='*50}")
        self.log("📊 RÉSUMÉ DES TESTS", "SUMMARY")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} {test_name}")
        
        self.log(f"\n🎯 RÉSULTAT GLOBAL: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 TOUS LES TESTS SONT PASSÉS ! L'API KYC CUSTOMER FONCTIONNE PARFAITEMENT", "SUCCESS")
        else:
            self.log(f"⚠️  {total-passed} test(s) ont échoué. Vérifiez les logs ci-dessus.", "WARNING")
        
        return passed == total


if __name__ == "__main__":
    print("Test de l'API KYC CUSTOMER XAMILA")
    print("=" * 60)
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Serveur Django accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Serveur Django non accessible: {e}")
        print("💡 Assurez-vous que le serveur Django fonctionne sur http://127.0.0.1:8000")
        exit(1)
    
    # Lancer les tests
    tester = XamilaAPITester()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
