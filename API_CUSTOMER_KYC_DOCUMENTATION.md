# API Documentation - CUSTOMER KYC System

## Vue d'ensemble

Le système KYC (Know Your Customer) XAMILA offre une solution complète d'authentification et de vérification d'identité pour les clients. Il inclut l'inscription sécurisée, la vérification OTP, la gestion de profils KYC, l'upload de documents et la vérification automatisée.

## Base URL
```
http://127.0.0.1:8000/api/customer/
```

## Authentification

Le système utilise JWT (JSON Web Tokens) pour l'authentification. Après connexion réussie, incluez le token dans l'en-tête :
```
Authorization: Bearer <access_token>
```

---

## 🔐 Endpoints d'Authentification

### 1. Inscription Client

**POST** `/customer/auth/register/`

Crée un nouveau compte client avec vérification OTP double (email + SMS).

**Body:**
```json
{
    "email": "client@example.com",
    "password": "MotDePasseSecurise123!",
    "phone": "+33123456789",
    "first_name": "Jean",
    "last_name": "Dupont"
}
```

**Réponse (201):**
```json
{
    "message": "Compte créé avec succès. Vérifiez votre email et SMS pour les codes OTP.",
    "user_id": "uuid-user-id",
    "email": "client@example.com",
    "phone": "+33123456789",
    "next_step": "verify_otp"
}
```

**Erreurs possibles:**
- `400`: Données manquantes ou invalides
- `400`: Email ou téléphone déjà utilisé
- `400`: Mot de passe trop faible

### 2. Vérification OTP

**POST** `/customer/auth/verify-otp/`

Vérifie les codes OTP reçus par email et SMS pour activer le compte.

**Body:**
```json
{
    "user_id": "uuid-user-id",
    "email_otp": "123456",
    "sms_otp": "789012"
}
```

**Réponse (200):**
```json
{
    "message": "Compte activé avec succès.",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid-user-id",
        "email": "client@example.com",
        "phone": "+33123456789",
        "first_name": "Jean",
        "last_name": "Dupont",
        "role": "CUSTOMER",
        "is_verified": false
    },
    "next_step": "complete_kyc"
}
```

### 3. Renvoyer OTP

**POST** `/customer/auth/resend-otp/`

Renvoie un code OTP (email ou SMS).

**Body:**
```json
{
    "user_id": "uuid-user-id",
    "otp_type": "email"  // ou "sms"
}
```

### 4. Connexion Client

**POST** `/customer/auth/login/`

Authentifie un client existant.

**Body:**
```json
{
    "email": "client@example.com",
    "password": "MotDePasseSecurise123!"
}
```

**Réponse (200):**
```json
{
    "message": "Connexion réussie.",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid-user-id",
        "email": "client@example.com",
        "phone": "+33123456789",
        "first_name": "Jean",
        "last_name": "Dupont",
        "role": "CUSTOMER",
        "is_verified": false,
        "kyc_status": "not_started",
        "kyc_completion": 0
    }
}
```

---

## 📋 Endpoints de Gestion KYC

### 5. Créer Profil KYC

**POST** `/customer/kyc/profile/create/`

**Authentification requise**

Crée le profil KYC initial du client.

**Body:**
```json
{
    "first_name": "Jean",
    "last_name": "Dupont",
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
    "identity_document_number": "123456789",
    "identity_document_expiry": "2030-05-15",
    "identity_document_issuing_country": "France",
    "occupation": "Ingénieur logiciel",
    "employer_name": "Tech Corp",
    "monthly_income": 4500.00,
    "source_of_funds": "SALARY"
}
```

**Réponse (201):**
```json
{
    "id": "uuid-kyc-profile-id",
    "user": "uuid-user-id",
    "full_name": "Jean Pierre Dupont",
    "kyc_status": "PENDING",
    "completion_percentage": 75,
    "is_kyc_complete": false,
    "created_at": "2025-08-10T13:00:00Z",
    // ... autres champs
}
```

### 6. Récupérer/Modifier Profil KYC

**GET/PUT** `/customer/kyc/profile/`

**Authentification requise**

Récupère ou modifie le profil KYC du client connecté.

**Réponse GET (200):**
```json
{
    "id": "uuid-kyc-profile-id",
    "user": "uuid-user-id",
    "user_email": "client@example.com",
    "user_phone": "+33123456789",
    "full_name": "Jean Pierre Dupont",
    "age": 35,
    "kyc_status": "PENDING",
    "completion_percentage": 75,
    "is_kyc_complete": false,
    "documents": [
        {
            "id": "uuid-doc-id",
            "document_type": "IDENTITY_FRONT",
            "verification_status": "PENDING",
            "uploaded_at": "2025-08-10T13:00:00Z"
        }
    ],
    // ... tous les champs du profil
}
```

### 7. Statut KYC Détaillé

**GET** `/customer/kyc/status/`

**Authentification requise**

Récupère le statut KYC détaillé avec les prochaines étapes.

**Réponse (200):**
```json
{
    "kyc_profile": {
        // Profil KYC complet
    },
    "required_documents": [
        {
            "type": "IDENTITY_FRONT",
            "name": "Pièce d'identité (recto)",
            "required": true
        },
        {
            "type": "SELFIE",
            "name": "Photo selfie",
            "required": true
        },
        {
            "type": "PROOF_OF_ADDRESS",
            "name": "Justificatif de domicile",
            "required": true
        }
    ],
    "next_steps": [
        "Téléverser les documents manquants",
        "Soumettre le profil pour révision"
    ]
}
```

---

## 📄 Endpoints de Gestion Documents

### 8. Upload Document KYC

**POST** `/customer/kyc/documents/upload/`

**Authentification requise**
**Content-Type:** `multipart/form-data`

Téléverse un document KYC (image ou PDF).

**Form Data:**
```
document_type: "IDENTITY_FRONT"  // IDENTITY_FRONT, IDENTITY_BACK, SELFIE, PROOF_OF_ADDRESS
file: [fichier binaire]
```

**Réponse (201):**
```json
{
    "id": "uuid-document-id",
    "document_type": "IDENTITY_FRONT",
    "file_url": "http://127.0.0.1:8000/media/kyc_documents/user_id/identity_front/uuid.jpg",
    "original_filename": "carte_identite.jpg",
    "file_size": 1024000,
    "file_size_mb": 1.02,
    "mime_type": "image/jpeg",
    "verification_status": "PENDING",
    "uploaded_at": "2025-08-10T13:00:00Z"
}
```

**Contraintes:**
- Taille max: 10MB
- Formats autorisés: JPEG, PNG, GIF, PDF, WebP
- Un seul document par type (remplace l'ancien)

### 9. Liste des Documents

**GET** `/customer/kyc/documents/`

**Authentification requise**

Liste tous les documents KYC du client.

**Réponse (200):**
```json
[
    {
        "id": "uuid-document-id",
        "document_type": "IDENTITY_FRONT",
        "verification_status": "VERIFIED",
        "auto_verification_score": 95.5,
        "uploaded_at": "2025-08-10T13:00:00Z",
        "verified_at": "2025-08-10T13:05:00Z"
    },
    // ... autres documents
]
```

### 10. Soumettre pour Révision

**POST** `/customer/kyc/submit/`

**Authentification requise**

Soumet le profil KYC complet pour révision par l'équipe.

**Body:** `{}` (vide)

**Réponse (200):**
```json
{
    "message": "Profil KYC soumis pour révision avec succès.",
    "status": "UNDER_REVIEW",
    "submitted_at": "2025-08-10T13:00:00Z"
}
```

**Prérequis:**
- Profil KYC complet
- Documents obligatoires téléversés (IDENTITY_FRONT, SELFIE, PROOF_OF_ADDRESS)

---

## 🔄 Flux Utilisateur Complet

### Étape 1: Inscription
```bash
POST /customer/auth/register/
# → Codes OTP envoyés par email et SMS
```

### Étape 2: Activation
```bash
POST /customer/auth/verify-otp/
# → Compte activé, tokens JWT reçus
```

### Étape 3: Création Profil KYC
```bash
POST /customer/kyc/profile/create/
# → Profil KYC créé (statut: PENDING)
```

### Étape 4: Upload Documents
```bash
POST /customer/kyc/documents/upload/  # Pièce d'identité
POST /customer/kyc/documents/upload/  # Selfie
POST /customer/kyc/documents/upload/  # Justificatif domicile
```

### Étape 5: Soumission
```bash
POST /customer/kyc/submit/
# → Profil soumis (statut: UNDER_REVIEW)
# → Vérification automatique déclenchée
```

### Étape 6: Résultat
```bash
GET /customer/kyc/status/
# → Statut final: APPROVED ou REJECTED
```

---

## 🛡️ Sécurité et Validation

### Validation des Données
- **Email**: Format valide, unicité
- **Téléphone**: Format international, unicité
- **Mot de passe**: Complexité Django (8+ caractères, mixte)
- **Date de naissance**: Âge minimum 18 ans, maximum 120 ans
- **Documents**: Taille max 10MB, formats autorisés

### Sécurité
- **JWT Tokens**: Expiration automatique
- **OTP**: Expiration 10 minutes, usage unique
- **Logs d'audit**: Toutes les actions KYC tracées
- **Permissions**: Accès restreint aux données du client connecté

### Vérification Automatique
- **Providers supportés**: Smile Identity, Onfido, ComplyAdvantage
- **Mode développement**: Mock verification avec scores simulés
- **Seuil d'approbation**: 80% par défaut (configurable)

---

## 📊 Codes de Statut

### Statuts KYC
- `PENDING`: En attente de completion
- `UNDER_REVIEW`: En cours de révision
- `APPROVED`: Approuvé ✅
- `REJECTED`: Rejeté (avec motif)
- `EXPIRED`: Expiré
- `SUSPENDED`: Suspendu

### Statuts Documents
- `PENDING`: En attente de vérification
- `PROCESSING`: En cours de traitement
- `VERIFIED`: Vérifié ✅
- `REJECTED`: Rejeté (avec motif)
- `EXPIRED`: Expiré

---

## 🧪 Tests et Développement

### Mode Mock (Développement)
```python
# settings.py
DEBUG = True
KYC_VERIFICATION_PROVIDER = 'mock'
KYC_AUTO_VERIFICATION_ENABLED = True
```

### Codes OTP en Développement
Les codes OTP sont affichés dans la console Django pour faciliter les tests.

### Données de Test
```json
{
    "email": "test@xamila.com",
    "password": "TestPassword123!",
    "phone": "+33123456789",
    "first_name": "Test",
    "last_name": "User"
}
```

---

## 🚨 Gestion d'Erreurs

### Erreurs Communes

**400 Bad Request**
```json
{
    "error": "Description de l'erreur",
    "details": ["Détail 1", "Détail 2"]
}
```

**401 Unauthorized**
```json
{
    "error": "Token d'authentification requis"
}
```

**403 Forbidden**
```json
{
    "error": "Accès non autorisé pour ce type de compte"
}
```

**404 Not Found**
```json
{
    "error": "Profil KYC non trouvé"
}
```

**500 Internal Server Error**
```json
{
    "error": "Erreur serveur interne",
    "details": "Description technique"
}
```

---

## 📧 Notifications Email

### Templates Disponibles
- **OTP Verification**: Code de vérification avec design responsive
- **KYC Approved**: Confirmation d'approbation
- **KYC Rejected**: Notification de rejet avec motifs
- **Welcome**: Email de bienvenue après activation

### Configuration SMTP
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'XAMILA <noreply@xamila.com>'
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Base de données
DB_NAME=xamila
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# KYC Providers
SMILE_IDENTITY_API_KEY=your_api_key
SMILE_IDENTITY_PARTNER_ID=your_partner_id
ONFIDO_API_KEY=your_api_key
COMPLY_ADVANTAGE_API_KEY=your_api_key

# Sécurité
SECRET_KEY=your-secret-key
KYC_AUTO_APPROVAL_SCORE=80
```

---

## 📈 Monitoring et Logs

### Logs d'Audit KYC
Tous les événements KYC sont enregistrés dans `KYCVerificationLog`:
- Création de profil
- Upload de documents
- Vérifications automatiques
- Approbations/Rejets
- Actions administratives

### Métriques Disponibles
- Taux de completion KYC
- Temps moyen de traitement
- Scores de vérification
- Taux d'approbation par provider

---

Cette documentation couvre l'ensemble du système KYC CUSTOMER de XAMILA. Pour toute question technique, consultez le code source ou contactez l'équipe de développement.
