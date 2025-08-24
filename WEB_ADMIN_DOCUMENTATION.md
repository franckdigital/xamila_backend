# 🔧 XAMILA WEB ADMIN - DOCUMENTATION COMPLÈTE
## Back-Office pour Administrateurs et Managers SGI

**Date** : 10 Janvier 2025  
**Version** : 1.0  
**Base URL** : `http://localhost:8000/api/admin/`

---

## 🎯 **APERÇU DU SYSTÈME WEB ADMIN**

L'interface Web Admin de XAMILA est un back-office complet permettant aux administrateurs de gérer l'ensemble de la plateforme fintech. Elle offre des fonctionnalités avancées de gestion des utilisateurs, SGI, contrats, contenu e-learning, et business intelligence.

### **Rôles et Permissions**
- ✅ **ADMIN** : Accès complet à toutes les fonctionnalités
- ✅ **SGI_MANAGER** : Accès limité à la gestion de leur SGI
- ✅ **INSTRUCTOR** : Accès à la gestion du contenu e-learning
- ✅ **SUPPORT** : Accès aux outils de support client

---

## 👥 **GESTION COMPLÈTE DES UTILISATEURS**

### 1. **Liste des Utilisateurs avec Filtres Avancés**

**Endpoint** : `GET /api/admin/users/`  
**Permissions** : `ADMIN`

#### **Paramètres de Filtrage**
- `role` : Filtrer par rôle (CUSTOMER, STUDENT, SGI_MANAGER, INSTRUCTOR, SUPPORT, ADMIN)
- `is_verified` : Filtrer par statut de vérification (true/false)
- `is_active` : Filtrer par statut d'activation (true/false)
- `country` : Filtrer par pays de résidence ou d'origine
- `search` : Recherche dans username, email, nom, prénom, téléphone
- `page` : Numéro de page (défaut: 1)
- `page_size` : Taille de page (défaut: 20, max: 100)

#### **Exemple de Requête**
```bash
GET /api/admin/users/?role=CUSTOMER&is_verified=true&country=Sénégal&page=1&page_size=20
```

#### **Réponse**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/admin/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid-here",
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "CUSTOMER",
            "is_active": true,
            "is_verified": true,
            "country_of_residence": "Sénégal",
            "created_at": "2025-01-10T12:00:00Z"
        }
    ],
    "statistics": {
        "total_users": 1500,
        "verified_users": 1200,
        "active_users": 1450,
        "verification_rate": 80.0,
        "role_distribution": {
            "CUSTOMER": 1200,
            "STUDENT": 200,
            "SGI_MANAGER": 50,
            "INSTRUCTOR": 30,
            "SUPPORT": 15,
            "ADMIN": 5
        },
        "recent_registrations": 25
    }
}
```

### 2. **Détails Complets d'un Utilisateur**

**Endpoint** : `GET /api/admin/users/{id}/`  
**Permissions** : `ADMIN`

#### **Réponse Détaillée**
```json
{
    "id": "uuid-here",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+221701234567",
    "role": "CUSTOMER",
    "is_active": true,
    "is_verified": true,
    "country_of_residence": "Sénégal",
    "created_at": "2025-01-10T12:00:00Z",
    "admin_details": {
        "connection_logs": {
            "last_login": "2025-01-10T15:30:00Z",
            "total_logins": 25,
            "active_sessions": 2
        },
        "otp_history": {
            "total_otp_sent": 3,
            "last_otp": "2025-01-10T12:05:00Z",
            "failed_attempts": 0
        },
        "account_activity": {
            "days_since_registration": 5,
            "profile_completion": 100.0
        },
        "sgi_info": null
    }
}
```

### 3. **Actions Administratives sur Utilisateurs**

**Endpoint** : `POST /api/admin/users/{id}/action/`  
**Permissions** : `ADMIN`

#### **Actions Disponibles**
- `activate` : Activer le compte
- `deactivate` : Désactiver le compte
- `verify` : Marquer comme vérifié
- `unverify` : Retirer la vérification
- `reset_password` : Réinitialiser le mot de passe
- `send_otp` : Envoyer un nouveau code OTP

#### **Payload**
```json
{
    "action": "activate",
    "reason": "Vérification manuelle effectuée"
}
```

#### **Réponse**
```json
{
    "message": "Compte activé. Raison: Vérification manuelle effectuée",
    "user": {
        "id": "uuid-here",
        "is_active": true,
        "updated_at": "2025-01-10T16:00:00Z"
    }
}
```

---

## 📊 **TABLEAU DE BORD ADMINISTRATEUR**

### **Statistiques Générales du Dashboard**

**Endpoint** : `GET /api/admin/dashboard/stats/`  
**Permissions** : `ADMIN`

#### **Métriques Complètes**
```json
{
    "users": {
        "total": 1500,
        "active": 1450,
        "verified": 1200,
        "verification_rate": 80.0,
        "new_today": 5,
        "new_week": 35,
        "new_month": 150,
        "by_role": {
            "CUSTOMER": {
                "name": "Client/Épargnant",
                "count": 1200,
                "active": 1180
            }
        }
    },
    "sgis": {
        "total": 50,
        "active": 45,
        "pending": 5,
        "approval_rate": 90.0
    },
    "contracts": {
        "total": 200,
        "pending": 25,
        "approved": 150,
        "approval_rate": 75.0
    },
    "otp": {
        "sent_today": 50,
        "success_rate": 85.0
    },
    "registration_evolution": [
        {
            "date": "2025-01-01",
            "count": 10
        }
    ]
}
```

---

## 🏦 **GESTION AVANCÉE DES SGI**

### 1. **Liste des SGI avec Informations Détaillées**

**Endpoint** : `GET /api/admin/sgis/`  
**Permissions** : `ADMIN`

#### **Filtres Disponibles**
- `status` : active, pending
- `search` : Nom SGI, description, email manager

#### **Réponse**
```json
{
    "sgis": [
        {
            "id": "uuid-here",
            "name": "SGI Excellence Afrique",
            "description": "Société de gestion spécialisée",
            "manager": {
                "id": "uuid-manager",
                "name": "Marie Diallo",
                "email": "marie@sgi-excellence.com",
                "phone": "+221701234567"
            },
            "is_active": true,
            "created_at": "2025-01-05T10:00:00Z",
            "contracts": {
                "total": 15,
                "pending": 3,
                "approved": 12
            }
        }
    ],
    "total_count": 50
}
```

### 2. **Analytics Avancées des SGI**

**Endpoint** : `GET /api/admin/sgis/analytics/`  
**Permissions** : `ADMIN`

#### **Métriques de Performance**
```json
{
    "overview": {
        "total_sgis": 50,
        "active_sgis": 45,
        "pending_sgis": 5,
        "activation_rate": 90.0
    },
    "performance_ranking": [
        {
            "sgi_id": "uuid-here",
            "sgi_name": "SGI Excellence",
            "manager": "Marie Diallo",
            "total_contracts": 15,
            "approved_contracts": 12,
            "approval_rate": 80.0,
            "total_investment": 50000000,
            "average_investment": 4166666.67
        }
    ],
    "top_performers": [],
    "registration_evolution": []
}
```

### 3. **Actions sur SGI**

**Endpoint** : `POST /api/admin/sgis/{id}/action/`  
**Permissions** : `ADMIN`

#### **Actions Disponibles**
- `approve` : Approuver la SGI
- `reject` : Rejeter la SGI
- `suspend` : Suspendre la SGI
- `reactivate` : Réactiver la SGI

### 4. **Actions en Lot sur SGI**

**Endpoint** : `POST /api/admin/sgis/bulk-action/`  
**Permissions** : `ADMIN`

#### **Payload**
```json
{
    "ids": ["uuid1", "uuid2", "uuid3"],
    "action": "approve",
    "reason": "Validation en lot après vérification"
}
```

---

## 📄 **GESTION AVANCÉE DES CONTRATS**

### 1. **Tableau de Bord des Contrats**

**Endpoint** : `GET /api/admin/contracts/dashboard/`  
**Permissions** : `ADMIN`

#### **Vue d'Ensemble Complète**
```json
{
    "overview": {
        "total_contracts": 200,
        "pending_contracts": 25,
        "approved_contracts": 150,
        "rejected_contracts": 25,
        "approval_rate": 75.0,
        "total_investment": 500000000.0,
        "average_investment": 3333333.33,
        "avg_processing_time_days": 5.2
    },
    "contracts_by_sgi": [
        {
            "sgi__name": "SGI Excellence",
            "sgi__id": "uuid-here",
            "total": 15,
            "approved": 12,
            "pending": 3,
            "total_amount": 50000000
        }
    ],
    "evolution": [
        {
            "date": "2025-01-01",
            "created": 5,
            "approved": 3,
            "rejected": 1
        }
    ]
}
```

### 2. **Liste Détaillée des Contrats**

**Endpoint** : `GET /api/admin/contracts/`  
**Permissions** : `ADMIN`

#### **Filtres Disponibles**
- `status` : PENDING, APPROVED, REJECTED
- `sgi_id` : ID de la SGI
- `min_amount` : Montant minimum
- `max_amount` : Montant maximum
- `search` : Email client, nom, SGI

#### **Réponse Paginée**
```json
{
    "contracts": [
        {
            "id": "uuid-here",
            "client": {
                "id": "uuid-client",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+221701234567"
            },
            "sgi": {
                "id": "uuid-sgi",
                "name": "SGI Excellence",
                "manager": "Marie Diallo"
            },
            "investment_amount": 5000000.0,
            "duration_months": 12,
            "status": "PENDING",
            "created_at": "2025-01-10T10:00:00Z",
            "processing_time_days": 2
        }
    ],
    "pagination": {
        "total_count": 200,
        "page": 1,
        "page_size": 20,
        "total_pages": 10
    }
}
```

### 3. **Actions sur Contrats**

**Endpoint** : `POST /api/admin/contracts/{id}/action/`  
**Permissions** : `ADMIN`

#### **Actions Disponibles**
- `approve` : Approuver le contrat
- `reject` : Rejeter le contrat
- `request_info` : Demander des informations supplémentaires

---

## 📚 **GESTION DU CONTENU E-LEARNING**

### **Statistiques du Contenu**

**Endpoint** : `GET /api/admin/content/stats/`  
**Permissions** : `ADMIN`

#### **Métriques Pédagogiques**
```json
{
    "questions": {
        "total": 500,
        "recent": 25,
        "by_category": [
            {
                "category": "Finance de base",
                "count": 150
            }
        ],
        "by_difficulty": [
            {
                "difficulty": "EASY",
                "count": 200
            }
        ],
        "by_type": [
            {
                "question_type": "MULTIPLE_CHOICE",
                "count": 300
            }
        ]
    }
}
```

---

## 📊 **BUSINESS INTELLIGENCE & ANALYTICS**

### **Métriques Avancées**

**Endpoint** : `GET /api/admin/bi/`  
**Permissions** : `ADMIN`

#### **Intelligence Business Complète**
```json
{
    "growth_metrics": {
        "user_growth_rate_monthly": 15.5,
        "new_users_current_month": 150,
        "new_users_last_month": 130
    },
    "engagement_metrics": {
        "active_users_7d": 800,
        "active_users_30d": 1200,
        "engagement_rate_7d": 53.33,
        "engagement_rate_30d": 80.0
    },
    "financial_metrics": {
        "total_investment": 500000000.0,
        "monthly_investment": 50000000.0,
        "average_contract_value": 3333333.33
    },
    "conversion_funnel": {
        "registration_to_verification": 80.0,
        "verification_to_contract": 12.5,
        "contract_to_approval": 75.0
    },
    "geographic_distribution": [
        {
            "country_of_residence": "Sénégal",
            "count": 800
        }
    ]
}
```

---

## 📋 **REPORTING ET EXPORTS**

### 1. **Export des Utilisateurs en CSV**

**Endpoint** : `GET /api/admin/export/users/`  
**Permissions** : `ADMIN`

#### **Filtres d'Export**
- `role` : Rôle spécifique
- `is_verified` : Statut de vérification
- `country` : Pays

#### **Réponse**
- Fichier CSV téléchargeable avec tous les détails utilisateurs
- Nom du fichier : `users_export_YYYYMMDD_HHMMSS.csv`

### 2. **Système de Matching SGI**

**Endpoint** : `GET /api/admin/matching/analytics/`  
**Permissions** : `ADMIN`

*Note : Système de matching à implémenter dans une version future*

---

## 🔒 **SÉCURITÉ ET PERMISSIONS**

### **Contrôle d'Accès**
- ✅ **Authentification JWT** obligatoire
- ✅ **Vérification du rôle ADMIN** sur tous les endpoints
- ✅ **Logs d'activité** pour audit
- ✅ **Rate limiting** pour prévenir les abus

### **Logs et Audit**

**Endpoint** : `GET /api/admin/logs/`  
**Permissions** : `ADMIN`

#### **Activités Tracées**
- Connexions utilisateurs
- Génération de codes OTP
- Actions administratives
- Modifications de données sensibles

---

## 🚀 **EXEMPLES D'UTILISATION**

### **1. Connexion Admin et Récupération du Token**
```bash
# Connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@xamila.com",
    "password": "AdminPassword123!"
  }'

# Réponse avec token
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### **2. Consultation du Dashboard**
```bash
curl -X GET http://localhost:8000/api/admin/dashboard/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **3. Gestion d'un Utilisateur**
```bash
# Désactiver un utilisateur
curl -X POST http://localhost:8000/api/admin/users/uuid-here/action/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "deactivate",
    "reason": "Activité suspecte détectée"
  }'
```

### **4. Approbation d'une SGI**
```bash
curl -X POST http://localhost:8000/api/admin/sgis/uuid-here/action/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "reason": "Documents validés"
  }'
```

---

## 🔧 **CONFIGURATION ET DÉPLOIEMENT**

### **Variables d'Environnement Requises**
```env
# Base de données
DATABASE_URL=mysql://user:password@localhost:3306/xamila_db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@xamila.com
EMAIL_HOST_PASSWORD=your-email-password

# Admin par défaut
DEFAULT_ADMIN_EMAIL=admin@xamila.com
DEFAULT_ADMIN_PASSWORD=AdminPassword123!
```

### **Commandes de Déploiement**
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer super utilisateur admin
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000
```

---

## 📈 **ROADMAP ET FONCTIONNALITÉS FUTURES**

### **Phase 2 - Fonctionnalités Avancées**
- 🔄 **Système de matching intelligent** SGI-Client
- 📧 **Notifications multi-canal** (Email, SMS, Push)
- 📊 **Rapports personnalisables** avec templates
- 🤖 **Intelligence artificielle** pour détection de fraude
- 📱 **Application mobile admin** pour gestion nomade

### **Phase 3 - Intégrations**
- 🏦 **APIs bancaires** partenaires
- 💳 **Systèmes de paiement** avancés
- 📋 **Outils de conformité** réglementaire
- 🔐 **Single Sign-On (SSO)** entreprise

---

*Cette documentation couvre l'ensemble des fonctionnalités Web Admin de la plateforme XAMILA. Elle sera mise à jour régulièrement avec les nouvelles fonctionnalités et améliorations.*
