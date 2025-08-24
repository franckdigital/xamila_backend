# 📚 Documentation API Xamila - Guide Complet

## 🎯 Vue d'ensemble

La plateforme fintech Xamila dispose maintenant d'une **documentation API interactive complète** générée automatiquement avec Swagger/OpenAPI (drf-spectacular).

## 🌐 Accès à la Documentation

### 📖 Interface Swagger UI (Recommandée)
- **URL** : `http://127.0.0.1:8000/api/docs/`
- **Description** : Interface interactive pour tester les APIs
- **Fonctionnalités** : 
  - Test des endpoints en temps réel
  - Authentification JWT intégrée
  - Exemples de requêtes/réponses
  - Validation automatique des données

### 📋 Interface ReDoc (Alternative)
- **URL** : `http://127.0.0.1:8000/api/docs/redoc/`
- **Description** : Documentation statique élégante
- **Avantages** : Présentation claire et navigation fluide

### 🔧 Schéma OpenAPI (JSON/YAML)
- **URL** : `http://127.0.0.1:8000/api/docs/schema/`
- **Description** : Schéma brut pour intégration avec d'autres outils
- **Utilisation** : Import dans Postman, Insomnia, etc.

## 🏗️ Architecture de l'API

### 🔐 Authentification
Toutes les APIs utilisent l'authentification **JWT (JSON Web Tokens)** :

1. **Inscription** → `POST /api/customer/auth/register/`
2. **Vérification OTP** → `POST /api/customer/auth/verify-otp/`
3. **Connexion** → `POST /api/customer/auth/login/`
4. **Utilisation** → Header : `Authorization: Bearer <token>`

### 📊 Endpoints Disponibles

#### 🔑 Authentication (Authentification)
- `POST /api/customer/auth/register/` - Inscription client
- `POST /api/customer/auth/verify-otp/` - Vérification OTP
- `POST /api/customer/auth/login/` - Connexion client
- `POST /api/customer/auth/resend-otp/` - Renvoyer OTP

#### 🆔 KYC (Know Your Customer)
- `POST /api/customer/kyc/profile/create/` - Créer profil KYC
- `GET /api/customer/kyc/profile/` - Récupérer profil KYC
- `PUT /api/customer/kyc/profile/` - Mettre à jour profil KYC
- `GET /api/customer/kyc/status/` - Statut KYC détaillé
- `POST /api/customer/kyc/documents/upload/` - Upload documents
- `GET /api/customer/kyc/documents/` - Liste des documents
- `POST /api/customer/kyc/submit/` - Soumettre pour révision

#### 🏦 SGI (Sociétés de Gestion d'Investissement)
- `GET /api/sgis/` - Liste des SGI
- `GET /api/sgis/{id}/` - Détails d'une SGI
- `POST /api/matching/` - Matching intelligent
- `GET /api/profile/` - Profil d'investissement client

## 🎨 Fonctionnalités de la Documentation

### ✨ Annotations Automatiques
- **Descriptions détaillées** pour chaque endpoint
- **Exemples de requêtes/réponses** 
- **Validation des schémas** en temps réel
- **Codes d'erreur** documentés

### 🏷️ Organisation par Tags
- **Authentication** : Endpoints d'authentification
- **KYC** : Gestion du profil KYC
- **SGI** : Gestion des SGI
- **Matching** : Système de matching
- **Admin** : Endpoints d'administration

### 🔒 Sécurité Intégrée
- **Authentification JWT** configurée
- **Permissions** documentées par endpoint
- **Scopes** et rôles utilisateurs

## 🚀 Utilisation Pratique

### 1. Tester l'API via Swagger UI

1. Accéder à `http://127.0.0.1:8000/api/docs/`
2. Cliquer sur "Authorize" en haut à droite
3. S'inscrire via `POST /api/customer/auth/register/`
4. Vérifier l'OTP via `POST /api/customer/auth/verify-otp/`
5. Copier le token JWT reçu
6. L'ajouter dans "Authorization" : `Bearer <token>`
7. Tester tous les autres endpoints authentifiés

### 2. Intégration avec Postman

1. Importer le schéma : `http://127.0.0.1:8000/api/docs/schema/`
2. Configurer l'authentification Bearer Token
3. Utiliser les collections générées automatiquement

### 3. Développement Frontend

```javascript
// Exemple d'utilisation avec JavaScript/React
const API_BASE = 'http://127.0.0.1:8000/api';

// Inscription
const register = async (userData) => {
  const response = await fetch(`${API_BASE}/customer/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
};

// Authentification avec token
const getKYCProfile = async (token) => {
  const response = await fetch(`${API_BASE}/customer/kyc/profile/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

## 📈 Codes de Statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| `200` | OK | Requête réussie |
| `201` | Created | Ressource créée avec succès |
| `400` | Bad Request | Erreur de validation des données |
| `401` | Unauthorized | Authentification requise |
| `403` | Forbidden | Permissions insuffisantes |
| `404` | Not Found | Ressource non trouvée |
| `500` | Internal Server Error | Erreur serveur |

## 🔧 Configuration Technique

### Packages Utilisés
- **drf-spectacular** : Génération automatique du schéma OpenAPI
- **djangorestframework** : Framework API REST
- **djangorestframework-simplejwt** : Authentification JWT

### Fichiers de Configuration
- `xamila/settings.py` : Configuration REST_FRAMEWORK et SPECTACULAR_SETTINGS
- `core/urls_swagger.py` : URLs de documentation
- `core/serializers_auth.py` : Serializers pour l'authentification
- `core/views_customer.py` : Vues avec annotations Swagger

## 🎯 Prochaines Étapes

### 📝 Extensions Prévues
- [ ] Annotations complètes pour tous les endpoints SGI
- [ ] Documentation des endpoints Admin
- [ ] Exemples de code pour différents langages
- [ ] Tests automatisés de la documentation
- [ ] Versioning de l'API

### 🚀 Déploiement
- Documentation accessible en production
- Mise à jour automatique lors des changements
- Intégration CI/CD pour validation du schéma

## 📞 Support

Pour toute question sur l'API :
- **Documentation** : `http://127.0.0.1:8000/api/docs/`
- **Schéma** : `http://127.0.0.1:8000/api/docs/schema/`
- **Contact** : api@xamila.com

---

**🎉 La documentation API Xamila est maintenant complète et interactive !**
