# Architecture Modulaire des Modèles Django XAMILA

## Vue d'ensemble

Cette documentation décrit l'architecture modulaire refactorisée des modèles Django pour la plateforme fintech XAMILA. L'objectif est d'éliminer les duplications, clarifier les responsabilités et améliorer la maintenabilité du code.

## Structure des Modules

### 1. **models_core.py** - Modèles de Base
**Responsabilité :** Entités fondamentales du système

#### Modèles inclus :
- **User** - Utilisateur personnalisé avec rôles multiples
- **UserProfile** - Profil utilisateur étendu
- **KYC** - Vérification d'identité (Know Your Customer)
- **RefreshToken** - Gestion des tokens JWT
- **OTP** - Codes de vérification temporaires
- **AuditLog** - Journal d'audit système

#### Rôles utilisateur supportés :
```python
USER_ROLES = [
    ('CUSTOMER', 'Client'),
    ('SGI_MANAGER', 'Manager SGI'),
    ('INSTRUCTOR', 'Formateur'),
    ('STUDENT', 'Étudiant'),
    ('SUPPORT', 'Support'),
    ('ADMIN', 'Administrateur'),
]
```

### 2. **models_sgi.py** - Modèles SGI Avancés
**Responsabilité :** Gestion complète des Sociétés de Gestion et d'Intermédiation

#### Modèles inclus :
- **SGI** - Société de Gestion et d'Intermédiation
- **SGIProfile** - Profil détaillé SGI
- **SGIService** - Services proposés par les SGI
- **SGIDocument** - Documents et certifications SGI
- **SGIRating** - Évaluations et notations SGI
- **ClientSGIInteraction** - Interactions clients-SGI
- **SGIContract** - Contrats SGI
- **ContractTemplate** - Templates de contrats
- **ContractClause** - Clauses contractuelles
- **ContractSignature** - Signatures électroniques
- **ContractAmendment** - Avenants aux contrats

#### Fonctionnalités clés :
- Gestion complète du cycle de vie des contrats
- Système de notation et d'évaluation
- Workflow de validation et d'approbation
- Signature électronique intégrée

### 3. **models_sgi_manager.py** - Outils Managers SGI
**Responsabilité :** Outils de gestion pour les managers SGI

#### Modèles inclus :
- **SGIManager** - Profil manager SGI
- **SGIManagerProfile** - Profil détaillé manager
- **SGIManagerPermission** - Permissions granulaires
- **SGIClientAssignment** - Attribution client-manager
- **SGIPerformanceMetric** - Métriques de performance
- **SGICommission** - Gestion des commissions
- **SGILeadManagement** - Gestion des prospects
- **SGIReporting** - Rapports et analytics
- **SGIAnalytics** - Analyses avancées

#### Fonctionnalités clés :
- Dashboard manager complet
- Gestion des performances et KPI
- Système de commissions automatisé
- Analytics et reporting avancés

### 4. **models_learning.py** - E-learning et Formations
**Responsabilité :** Système d'apprentissage et de certification

#### Modèles inclus :
- **LearningPath** - Parcours d'apprentissage
- **LearningModule** - Modules de formation
- **QuizExtended** - Quiz avancés
- **QuestionExtended** - Questions étendues
- **StudentProgress** - Suivi des progrès
- **ModuleCompletion** - Completion des modules
- **QuizAttempt** - Tentatives de quiz
- **Certification** - Certifications obtenues

#### Types de questions supportés :
- Choix multiple/unique
- Vrai/Faux
- Saisie de texte
- Numérique
- Appariement
- Classement
- Texte à trous

#### Fonctionnalités clés :
- Parcours d'apprentissage personnalisés
- Système de certification complet
- Suivi détaillé des progrès
- Analytics d'apprentissage

### 5. **models_trading.py** - Trading et Simulation Boursière
**Responsabilité :** Simulation de trading et gestion de portefeuilles

#### Modèles inclus :
- **StockExtended** - Actions avec données avancées
- **Portfolio** - Portefeuilles virtuels
- **Holding** - Positions détenues
- **TradingOrder** - Ordres de trading
- **Transaction** - Historique des transactions
- **PriceHistory** - Historique des prix OHLCV
- **TradingCompetition** - Compétitions de trading
- **CompetitionParticipant** - Participants aux compétitions

#### Types d'ordres supportés :
- Ordre au marché
- Ordre à cours limité
- Ordre stop
- Ordre stop-limit

#### Fonctionnalités clés :
- Simulation de trading réaliste
- Gestion de portefeuilles avancée
- Compétitions et classements
- Historique complet des prix

### 6. **models_notifications.py** - Système de Notifications
**Responsabilité :** Notifications multi-canal et campagnes

#### Modèles inclus :
- **NotificationTemplate** - Templates réutilisables
- **NotificationCampaign** - Campagnes de notifications
- **Notification** - Notifications individuelles
- **NotificationPreference** - Préférences utilisateur
- **NotificationLog** - Journal des notifications
- **WebhookEndpoint** - Endpoints webhook
- **NotificationQueue** - File d'attente

#### Canaux supportés :
- Email
- SMS
- Notifications push
- Notifications in-app
- Webhooks

#### Fonctionnalités clés :
- Système de templates avancé
- Campagnes automatisées
- Préférences utilisateur granulaires
- Analytics de campagnes

## Architecture et Relations

### Diagramme des Relations Principales

```
User (Core)
├── UserProfile (Core)
├── KYC (Core)
├── SGIManager (SGI Manager)
├── StudentProgress (Learning)
├── Portfolio (Trading)
├── NotificationPreference (Notifications)
└── Certifications (Learning)

SGI (SGI)
├── SGIProfile (SGI)
├── SGIService (SGI)
├── SGIDocument (SGI)
├── SGIContract (SGI)
└── SGIManager (SGI Manager)

LearningPath (Learning)
├── LearningModule (Learning)
├── QuizExtended (Learning)
└── StudentProgress (Learning)

Portfolio (Trading)
├── Holding (Trading)
├── TradingOrder (Trading)
└── Transaction (Trading)
```

## Intégration Django

### Configuration dans settings.py

```python
INSTALLED_APPS = [
    # ... autres apps
    'core',
    # ... 
]

# Import des modèles consolidés
from core.models_consolidated import *
```

### Migrations

```bash
# Créer les migrations
python manage.py makemigrations core

# Appliquer les migrations
python manage.py migrate
```

## Avantages de cette Architecture

### 1. **Séparation des Responsabilités**
- Chaque module a une responsabilité claire
- Facilite la maintenance et les évolutions
- Améliore la lisibilité du code

### 2. **Élimination des Duplications**
- Modèles unifiés et cohérents
- Réutilisation des composants
- Réduction de la dette technique

### 3. **Modularité**
- Développement en équipes parallèles
- Tests unitaires ciblés
- Déploiements modulaires

### 4. **Extensibilité**
- Ajout facile de nouveaux modules
- Extension des modèles existants
- Intégration d'APIs externes

### 5. **Performance**
- Optimisation des requêtes par module
- Index ciblés
- Mise en cache granulaire

## Bonnes Pratiques

### 1. **Conventions de Nommage**
```python
# Modèles : PascalCase
class SGIManager(models.Model):
    pass

# Champs : snake_case
investment_amount = models.DecimalField(...)

# Relations : descriptives
related_name='sgi_contracts'
```

### 2. **Validation des Données**
```python
# Utiliser les validators Django
from django.core.validators import MinValueValidator, MaxValueValidator

amount = models.DecimalField(
    validators=[MinValueValidator(Decimal('0.01'))]
)
```

### 3. **Métadonnées Systématiques**
```python
class Meta:
    verbose_name = "Nom singulier"
    verbose_name_plural = "Nom pluriel"
    ordering = ['-created_at']
    indexes = [
        models.Index(fields=['field1', 'field2']),
    ]
```

### 4. **Méthodes Utilitaires**
```python
def __str__(self):
    return f"{self.name} - {self.status}"

@property
def calculated_field(self):
    # Calculs dérivés
    return self.field1 + self.field2
```

## Tests et Validation

### Structure des Tests
```
tests/
├── test_core_models.py
├── test_sgi_models.py
├── test_sgi_manager_models.py
├── test_learning_models.py
├── test_trading_models.py
└── test_notifications_models.py
```

### Exemple de Test
```python
from django.test import TestCase
from core.models_consolidated import User, SGI, Portfolio

class SGIModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            role='SGI_MANAGER'
        )
    
    def test_sgi_creation(self):
        sgi = SGI.objects.create(
            name='Test SGI',
            registration_number='SGI001'
        )
        self.assertEqual(sgi.name, 'Test SGI')
```

## Déploiement et Monitoring

### 1. **Migrations en Production**
```bash
# Vérifier les migrations
python manage.py showmigrations

# Appliquer avec sauvegarde
python manage.py migrate --fake-initial
```

### 2. **Monitoring des Performances**
- Utiliser Django Debug Toolbar en développement
- Monitoring des requêtes lentes
- Alertes sur les erreurs de validation

### 3. **Sauvegarde des Données**
```bash
# Export des données
python manage.py dumpdata core > backup.json

# Import des données
python manage.py loaddata backup.json
```

## Roadmap et Évolutions

### Phase 1 : Implémentation de Base ✅
- [x] Création des modules spécialisés
- [x] Définition des modèles
- [x] Documentation architecture

### Phase 2 : Intégration Django
- [ ] Migrations et tests
- [ ] Endpoints API REST
- [ ] Documentation API (Swagger)

### Phase 3 : Fonctionnalités Avancées
- [ ] Système de permissions granulaires
- [ ] Analytics et reporting
- [ ] Intégrations externes

### Phase 4 : Optimisation
- [ ] Performance et mise en cache
- [ ] Monitoring et alertes
- [ ] Déploiement automatisé

## Support et Maintenance

### Contacts Équipe
- **Architecture :** Équipe Backend
- **SGI :** Équipe Business
- **Learning :** Équipe Éducation
- **Trading :** Équipe Fintech
- **Notifications :** Équipe DevOps

### Documentation Complémentaire
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Testing Guide](./TESTING.md)
- [Performance Guide](./PERFORMANCE.md)

---

*Cette architecture modulaire constitue la base technique robuste pour l'évolution de la plateforme XAMILA vers une solution fintech complète et scalable.*
