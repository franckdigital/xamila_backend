# 🔐 XAMILA - DOCUMENTATION API AUTHENTIFICATION & RÔLES
## Système d'Enregistrement Multi-Rôles

**Date** : 10 Janvier 2025  
**Version** : 1.0  
**Base URL** : `http://localhost:8000/api/`

---

## 🎯 **APERÇU DU SYSTÈME DE RÔLES**

La plateforme XAMILA dispose de **6 rôles utilisateur** distincts avec des fonctionnalités spécifiques :

| Rôle | Code | Description | Accès |
|------|------|-------------|-------|
| **Client/Épargnant** | `CUSTOMER` | Utilisateur final (défaut) | Public |
| **Étudiant/Apprenant** | `STUDENT` | Participant aux formations | Public |
| **Manager SGI** | `SGI_MANAGER` | Gestionnaire de SGI | Public + Validation |
| **Instructeur** | `INSTRUCTOR` | Formateur/Créateur de contenu | Public + Validation |
| **Support Client** | `SUPPORT` | Agent de support | Public + Validation |
| **Administrateur** | `ADMIN` | Super utilisateur | Admin seulement |

---

## 📋 **ENDPOINTS D'ENREGISTREMENT**

### 1. **Enregistrement Client/Épargnant** (Public)

**Endpoint** : `POST /api/auth/register/customer/`  
**Permissions** : Aucune (public)  
**Rôle attribué** : `CUSTOMER` (par défaut)

#### **Payload Requis**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal"
}
```

#### **Réponse Succès (201)**
```json
{
    "message": "Inscription réussie. Un code de vérification a été envoyé à votre email.",
    "user_id": "uuid-here",
    "email_sent": true,
    "user": {
        "id": "uuid-here",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+221701234567",
        "role": "CUSTOMER",
        "country_of_residence": "Sénégal",
        "country_of_origin": "Sénégal",
        "is_verified": false,
        "email_verified": false,
        "phone_verified": false,
        "created_at": "2025-01-10T12:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
    }
}
```

### 2. **Enregistrement Étudiant/Apprenant** (Public)

**Endpoint** : `POST /api/auth/register/student/`  
**Permissions** : Aucune (public)  
**Rôle attribué** : `STUDENT`

#### **Payload Requis**
```json
{
    "username": "student_marie",
    "email": "marie@student.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "Marie",
    "last_name": "Ndiaye",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal",
    "education_level": "Baccalauréat",
    "interests": "Finance, Épargne, Investissement"
}
```

#### **Réponse Succès (201)**
```json
{
    "message": "Inscription Étudiant réussie. Un code de vérification a été envoyé à votre email.",
    "user_id": "uuid-here",
    "email_sent": true,
    "user": {
        "id": "uuid-here",
        "username": "student_marie",
        "email": "marie@student.com",
        "first_name": "Marie",
        "last_name": "Ndiaye",
        "phone": "+221701234567",
        "role": "STUDENT",
        "country_of_residence": "Sénégal",
        "country_of_origin": "Sénégal",
        "is_verified": false,
        "email_verified": false,
        "phone_verified": false,
        "created_at": "2025-01-10T12:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
    },
    "note": "Vous pouvez maintenant accéder aux formations disponibles."
}
```

### 3. **Enregistrement Manager SGI** (Public + Création SGI)

**Endpoint** : `POST /api/auth/register/sgi-manager/`  
**Permissions** : Aucune (public)  
**Rôle attribué** : `SGI_MANAGER`  
**Action supplémentaire** : Création automatique d'une SGI

#### **Payload Requis**
```json
{
    "username": "sgi_manager",
    "email": "manager@sgi-example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "Marie",
    "last_name": "Diallo",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal",
    "sgi_name": "SGI Excellence Afrique",
    "sgi_description": "Société de gestion d'investissement spécialisée dans les marchés africains",
    "sgi_address": "123 Avenue Léopold Sédar Senghor, Dakar, Sénégal",
    "sgi_website": "https://sgi-excellence.com"
}
```

#### **Réponse Succès (201)**
```json
{
    "message": "Inscription Manager SGI réussie. Un code de vérification a été envoyé à votre email.",
    "user_id": "uuid-here",
    "email_sent": true,
    "user": {
        "id": "uuid-here",
        "username": "sgi_manager",
        "email": "manager@sgi-example.com",
        "role": "SGI_MANAGER",
        // ... autres champs
    },
    "note": "Votre SGI a été créée et sera vérifiée par notre équipe."
}
```

### 3. **Enregistrement Instructeur/Formateur** (Public + Validation)

**Endpoint** : `POST /api/auth/register/instructor/`  
**Permissions** : Aucune (public)  
**Rôle attribué** : `INSTRUCTOR`

#### **Payload Requis**
```json
{
    "username": "prof_finance",
    "email": "prof@example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "Amadou",
    "last_name": "Ba",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal",
    "specialization": "Finance d'entreprise et marchés financiers",
    "bio": "Expert en finance avec 15 ans d'expérience dans l'enseignement"
}
```

### 4. **Enregistrement Support Client** (Public + Validation)

**Endpoint** : `POST /api/auth/register/support/`  
**Permissions** : Aucune (public)  
**Rôle attribué** : `SUPPORT`

#### **Payload Requis**
```json
{
    "username": "support_agent",
    "email": "support@example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "Fatou",
    "last_name": "Sall",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal",
    "department": "Support Technique"
}
```

---

## 👨‍💼 **ENDPOINTS ADMIN POUR CRÉATION D'UTILISATEURS**

### 1. **Création d'Utilisateur par l'Admin**

**Endpoint** : `POST /api/auth/admin/users/create/`  
**Permissions** : `ADMIN` seulement  
**Rôle attribué** : Selon le choix de l'admin

#### **Payload Requis**
```json
{
    "username": "new_user",
    "email": "newuser@example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "first_name": "Nouveau",
    "last_name": "Utilisateur",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal",
    "country_of_origin": "Sénégal",
    "role": "INSTRUCTOR",
    "is_active": true
}
```

#### **Réponse Succès (201)**
```json
{
    "id": "uuid-here",
    "username": "new_user",
    "email": "newuser@example.com",
    "role": "INSTRUCTOR",
    "is_active": true,
    // ... autres champs
}
```

### 2. **Liste de Tous les Utilisateurs**

**Endpoint** : `GET /api/auth/admin/users/`  
**Permissions** : `ADMIN` seulement

#### **Réponse Succès (200)**
```json
[
    {
        "id": "uuid-1",
        "username": "user1",
        "email": "user1@example.com",
        "role": "CUSTOMER",
        "is_verified": true,
        "created_at": "2025-01-10T12:00:00Z"
    },
    {
        "id": "uuid-2",
        "username": "user2",
        "email": "user2@example.com",
        "role": "SGI_MANAGER",
        "is_verified": false,
        "created_at": "2025-01-10T11:00:00Z"
    }
    // ... autres utilisateurs
]
```

---

## ✅ **ENDPOINTS DE VÉRIFICATION**

### 1. **Vérification Code OTP**

**Endpoint** : `POST /api/auth/verify-otp/`  
**Permissions** : Aucune (public)

#### **Payload Requis**
```json
{
    "user_id": "uuid-here",
    "otp_code": "123456"
}
```

#### **Réponse Succès (200)**
```json
{
    "message": "Compte activé avec succès",
    "user": {
        "id": "uuid-here",
        "username": "john_doe",
        "email": "john@example.com",
        "role": "CUSTOMER",
        "is_verified": true,
        "email_verified": true
    },
    "tokens": {
        "refresh": "refresh-token-here",
        "access": "access-token-here"
    }
}
```

### 2. **Renvoyer Code OTP**

**Endpoint** : `POST /api/auth/resend-otp/`  
**Permissions** : Aucune (public)

#### **Payload Requis**
```json
{
    "user_id": "uuid-here"
}
```

#### **Réponse Succès (200)**
```json
{
    "message": "Nouveau code OTP envoyé",
    "email_sent": true
}
```

---

## 🔑 **ENDPOINTS DE CONNEXION**

### 1. **Connexion Utilisateur**

**Endpoint** : `POST /api/auth/login/`  
**Permissions** : Aucune (public)

#### **Payload Requis**
```json
{
    "email": "john@example.com",
    "password": "MotDePasse123!"
}
```

#### **Réponse Succès (200)**
```json
{
    "message": "Connexion réussie",
    "user": {
        "id": "uuid-here",
        "username": "john_doe",
        "email": "john@example.com",
        "role": "CUSTOMER",
        "is_verified": true
    },
    "tokens": {
        "refresh": "refresh-token-here",
        "access": "access-token-here"
    }
}
```

### 2. **Profil Utilisateur Connecté**

**Endpoint** : `GET /api/auth/profile/`  
**Permissions** : Authentifié  
**Headers** : `Authorization: Bearer access-token-here`

#### **Réponse Succès (200)**
```json
{
    "user": {
        "id": "uuid-here",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+221701234567",
        "role": "CUSTOMER",
        "country_of_residence": "Sénégal",
        "country_of_origin": "Sénégal",
        "is_verified": true,
        "email_verified": true,
        "phone_verified": false,
        "created_at": "2025-01-10T12:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
    }
}
```

### 3. **Mise à Jour Profil**

**Endpoint** : `PUT /api/auth/profile/update/`  
**Permissions** : Authentifié  
**Headers** : `Authorization: Bearer access-token-here`

#### **Payload (Partiel)**
```json
{
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+221701234568",
    "country_of_residence": "Mali"
}
```

---

## 🔒 **GESTION DES PERMISSIONS**

### **Matrice des Permissions par Rôle**

| Fonctionnalité | CUSTOMER | STUDENT | SGI_MANAGER | INSTRUCTOR | SUPPORT | ADMIN |
|----------------|----------|---------|-------------|------------|---------|-------|
| **Inscription publique** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Création par admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Accès formations** | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Gestion SGI** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Création contenu** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Support client** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Administration** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### **Workflow de Validation**

1. **CUSTOMER** : Activation immédiate après vérification OTP
2. **STUDENT** : Activation immédiate après vérification OTP (accès formations)
3. **SGI_MANAGER** : Vérification OTP + Validation manuelle de la SGI
4. **INSTRUCTOR** : Vérification OTP + Validation manuelle des qualifications
5. **SUPPORT** : Vérification OTP + Validation manuelle par RH
6. **ADMIN** : Création directe par un autre admin

---

## 📧 **SYSTÈME OTP ET NOTIFICATIONS**

### **Types de Codes OTP**
- `REGISTRATION` : Activation de compte (10 minutes)
- `PASSWORD_RESET` : Réinitialisation mot de passe (10 minutes)
- `EMAIL_VERIFICATION` : Vérification email (10 minutes)

### **Templates Email Automatiques**
- Email de bienvenue avec code OTP
- Confirmation d'inscription par rôle
- Notifications aux équipes internes
- Rappels de vérification

---

## 🚨 **CODES D'ERREUR COMMUNS**

| Code | Message | Description |
|------|---------|-------------|
| **400** | `Les mots de passe ne correspondent pas` | Passwords mismatch |
| **400** | `Email déjà utilisé` | Email already exists |
| **400** | `Code OTP invalide ou déjà utilisé` | Invalid/used OTP |
| **400** | `Code OTP expiré` | Expired OTP |
| **401** | `Compte non activé` | Account not activated |
| **401** | `Email ou mot de passe incorrect` | Invalid credentials |
| **403** | `Permission refusée` | Insufficient permissions |
| **404** | `Utilisateur non trouvé` | User not found |

---

## 🧪 **EXEMPLES DE TESTS**

### **Test d'Enregistrement Client**
```bash
curl -X POST http://localhost:8000/api/auth/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_client",
    "email": "client@test.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "Client",
    "phone": "+221701234567",
    "country_of_residence": "Sénégal"
  }'
```

### **Test de Connexion**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@test.com",
    "password": "TestPass123!"
  }'
```

### **Test de Profil (avec token)**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 📝 **NOTES IMPORTANTES**

1. **Rôle par défaut** : `CUSTOMER` pour tous les nouveaux utilisateurs
2. **Validation manuelle** : SGI_MANAGER, INSTRUCTOR, SUPPORT nécessitent une validation admin
3. **Création admin** : Seuls les admins peuvent créer d'autres utilisateurs via l'interface admin
4. **Sécurité** : Tous les mots de passe sont hashés avec Django's PBKDF2
5. **Tokens JWT** : Expiration configurable, refresh tokens supportés
6. **Emails** : Configuration SMTP requise pour l'envoi des codes OTP

---

*Cette documentation couvre l'ensemble du système d'authentification et de gestion des rôles de la plateforme XAMILA. Pour plus d'informations, consultez le document XAMILA_FONCTIONNALITES_COMPLETES.md*
