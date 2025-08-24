# Configuration Swagger/OpenAPI pour la plateforme Xamila
# À ajouter dans settings.py

SPECTACULAR_SETTINGS = {
    'TITLE': 'Xamila Fintech Platform API',
    'DESCRIPTION': '''API complète de la plateforme fintech Xamila

## Fonctionnalités principales

### 🔐 Authentification et KYC
- Inscription et connexion sécurisées
- Vérification OTP (email + SMS)
- Gestion complète du profil KYC
- Upload et validation de documents

### 🏦 Gestion SGI (Sociétés de Gestion d'Investissement)
- Enregistrement et validation des SGI
- Gestion des managers SGI
- Matching intelligent clients-SGI
- Suivi des performances

### 📊 Fonctionnalités avancées
- Système de matching basé sur les critères
- Notifications automatiques
- Reporting et analytics
- Gestion des contrats

## Authentification

Cette API utilise JWT (JSON Web Tokens) pour l'authentification.

1. **Inscription** : `POST /api/customer/auth/register/`
2. **Vérification OTP** : `POST /api/customer/auth/verify-otp/`
3. **Connexion** : `POST /api/customer/auth/login/`
4. **Utilisation** : Inclure le token dans l'en-tête : `Authorization: Bearer <token>`

## Codes de statut

- `200` : Succès
- `201` : Créé avec succès
- `400` : Erreur de validation
- `401` : Non authentifié
- `403` : Non autorisé
- `404` : Ressource non trouvée
- `500` : Erreur serveur
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'Équipe Xamila',
        'email': 'api@xamila.com',
    },
    'LICENSE': {
        'name': 'Propriétaire',
    },
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'Endpoints d\'authentification (inscription, connexion, OTP)'
        },
        {
            'name': 'KYC',
            'description': 'Gestion du profil KYC et des documents'
        },
        {
            'name': 'SGI',
            'description': 'Gestion des Sociétés de Gestion d\'Investissement'
        },
        {
            'name': 'Matching',
            'description': 'Système de matching intelligent clients-SGI'
        },
        {
            'name': 'Admin',
            'description': 'Endpoints d\'administration'
        },
    ],
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'ENABLE_DJANGO_DEPLOY_CHECK': False,
    'DISABLE_ERRORS_AND_WARNINGS': True,
}
