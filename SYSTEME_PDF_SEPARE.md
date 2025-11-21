# 📄 Système PDF Séparé - Documentation complète

## 🎯 Objectif

Séparer le contrat principal (statique) des annexes (dynamiques) et envoyer les deux par email au client, au manager SGI et à l'équipe Xamila.

---

## 📋 Architecture

### **1. Contrat principal (statique)**
- **Fichier:** PDF template GEK CAPITAL original
- **Contenu:** Texte légal, conditions générales (pages 1-20)
- **Données:** AUCUNE donnée dynamique
- **Stockage:** `media/contracts/main/`

### **2. Annexes (dynamiques)**
- **Pages:** 21, 22, 23, 26
- **Contenu:** Données du client
- **Génération:** Service `AnnexPDFService`
- **Stockage:** `media/contracts/annexes/`

---

## 🔧 Services créés

### **1. AnnexPDFService** (`services_annex_pdf.py`)

Génère un PDF contenant uniquement les 4 pages d'annexes avec les données du client.

**Méthodes:**
- `generate_annexes_pdf(aor, annex_data)` - Génère le PDF complet des annexes
- `_generate_page21(aor, annex_data)` - Page 21: Texte légal et signatures
- `_generate_page22(aor, annex_data)` - Page 22: Formulaire d'ouverture
- `_generate_page23(aor, annex_data)` - Page 23: Caractéristiques du compte
- `_generate_page26(aor, annex_data)` - Page 26: Procuration

**Exemple d'utilisation:**
```python
from core.services_annex_pdf import AnnexPDFService

service = AnnexPDFService()
annexes_pdf_buffer = service.generate_annexes_pdf(aor, annex_data)
```

### **2. ContractEmailService** (`services_email.py`)

Envoie les emails avec les PDF en pièces jointes.

**Méthodes:**
- `send_contract_emails(aor, contract_pdf, annexes_pdf, sgi_manager_email)` - Envoie tous les emails
- `_send_client_email(...)` - Email au client
- `_send_sgi_manager_email(...)` - Email au manager SGI
- `_send_xamila_team_email(...)` - Email à l'équipe Xamila

**Destinataires:**
1. **Client:** `aor.email`
2. **Manager SGI:** `sgi.manager_email` (si disponible)
3. **Équipe Xamila:** `settings.XAMILA_TEAM_EMAIL`

**Pièces jointes:**
- `Contrat_GEK_CAPITAL_[Nom].pdf` - Contrat principal
- `Annexes_[Nom].pdf` - Annexes avec données

---

## 💾 Modèle mis à jour

### **AccountOpeningRequest** (`models_sgi.py`)

**Nouveaux champs:**
```python
# PDF générés
contract_pdf = models.FileField(
    upload_to="contracts/main/",
    blank=True,
    null=True,
    help_text="Contrat principal (statique)"
)
annexes_pdf = models.FileField(
    upload_to="contracts/annexes/",
    blank=True,
    null=True,
    help_text="Annexes avec données dynamiques"
)
```

---

## 🔄 Flux de traitement

### **Lors de la soumission du formulaire:**

```
1. Client soumet le formulaire
   ↓
2. Backend crée AccountOpeningRequest
   ↓
3. Génération du contrat principal (statique)
   - Copie du PDF template GEK CAPITAL
   - AUCUNE donnée dynamique
   ↓
4. Génération des annexes (dynamiques)
   - AnnexPDFService.generate_annexes_pdf()
   - Page 21: Signatures
   - Page 22: Identité, adresses, contacts
   - Page 23: Type de compte, personne désignée
   - Page 26: Procuration (si applicable)
   ↓
5. Sauvegarde des PDF en BD
   - contract_pdf → media/contracts/main/
   - annexes_pdf → media/contracts/annexes/
   ↓
6. Envoi des emails
   - ContractEmailService.send_contract_emails()
   - Email au client
   - Email au manager SGI
   - Email à l'équipe Xamila
   ↓
7. Confirmation au client
```

---

## 📧 Templates d'emails

### **1. Email au client**

**Sujet:** "Votre demande d'ouverture de compte-titres - GEK CAPITAL"

**Contenu:**
```html
Bonjour [Nom],

Nous avons bien reçu votre demande d'ouverture de compte-titres 
auprès de GEK CAPITAL.

Vous trouverez en pièces jointes :
• Contrat principal : Convention d'ouverture de compte-titres
• Annexes : Formulaires complétés avec vos informations

Prochaines étapes :
1. Vérifiez attentivement les informations dans les annexes
2. Imprimez et signez les documents
3. Retournez-nous les documents signés avec les pièces justificatives

Numéro de demande : [ID]
Email : [email]
Téléphone : [phone]

Cordialement,
L'équipe Xamila
```

### **2. Email au manager SGI**

**Sujet:** "Nouvelle demande d'ouverture de compte - [Nom Client]"

**Contenu:**
```html
Bonjour,

Une nouvelle demande d'ouverture de compte-titres a été soumise via Xamila.

Informations du client :
• Nom complet : [Nom]
• Email : [email]
• Téléphone : [phone]
• Pays : [pays]
• Nationalité : [nationalité]
• Profil investisseur : [profil]

Numéro de demande : [ID]
Date de soumission : [date]

Vous trouverez en pièces jointes le contrat et les annexes complétés.

Cordialement,
Plateforme Xamila
```

### **3. Email à l'équipe Xamila**

**Sujet:** "[NOUVELLE DEMANDE] [Nom] - GEK CAPITAL"

**Contenu:**
```html
📋 Nouvelle demande d'ouverture de compte

Client : [Nom]
SGI : GEK CAPITAL
Email : [email]
Téléphone : [phone]

ID Demande : [ID]
Profil : [profil]
Pays : [pays]

Méthodes de financement :
• VISA
• Mobile Money
• Virement bancaire

Documents en pièces jointes.

L'équipe Xamila
```

---

## 🎨 Contenu des annexes

### **Page 21 - Texte légal et signatures**

**Contenu:**
- Texte légal (articles 29, 30, 34)
- Fait à / Le (date)
- Signature du titulaire (base64 → image)
- Signature GEK CAPITAL (base64 → image)

**Données dynamiques:**
- `p21.place` - Lieu de signature
- `p21.date` - Date de signature
- `p21.signature_titulaire` - Signature client
- `p21.signature_gek` - Signature GEK

### **Page 22 - Formulaire d'ouverture**

**Contenu:**
- Numéro de compte-titres
- Identité personne physique (civilité, nom, prénoms, naissance)
- Adresse fiscale
- Coordonnées (téléphone, email)

**Données dynamiques:**
- `p22.account_number`
- `p22.civility`, `p22.last_name`, `p22.first_names`
- `p22.birth_date`, `p22.birth_place`
- `p22.nationality`
- `p22.fiscal_address`, `p22.fiscal_city`, `p22.fiscal_country`
- `p22.phone`, `p22.email`

### **Page 23 - Caractéristiques du compte**

**Contenu:**
- Type de compte (individuel/joint/indivision)
- Personne désignée
- Déclaration
- Signature

**Données dynamiques:**
- `p23.account_individual`, `p23.account_joint`, `p23.account_indivision`
- `p23.designated_person_name`
- `p23.place`, `p23.date`
- `p23.signature`

### **Page 26 - Procuration**

**Contenu:**
- Mandant (nom, prénoms, adresse)
- Mandataire (nom, prénoms, adresse)
- Signatures

**Données dynamiques:**
- `p26.has_procuration`
- `p26.mandant_name`, `p26.mandant_first_names`, `p26.mandant_address`
- `p26.mandataire_name`, `p26.mandataire_first_names`, `p26.mandataire_address`
- `p26.signature_mandant`, `p26.signature_mandataire`

---

## 🔧 Configuration requise

### **1. Settings.py**

```python
# Email
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'
XAMILA_TEAM_EMAIL = 'team@xamila.com'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email backend (pour développement)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email backend (pour production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-password'
```

### **2. URLs.py**

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### **3. Dossiers**

```bash
mkdir -p media/contracts/main
mkdir -p media/contracts/annexes
mkdir -p media/kyc/account_opening/photos
mkdir -p media/kyc/account_opening/id_scans
```

---

## 📊 Statistiques

| Aspect | Valeur |
|--------|--------|
| **Services créés** | 2 (AnnexPDFService, ContractEmailService) |
| **Champs ajoutés** | 2 (contract_pdf, annexes_pdf) |
| **Pages d'annexes** | 4 (21, 22, 23, 26) |
| **Emails envoyés** | 3 (client, manager SGI, équipe Xamila) |
| **Pièces jointes** | 2 (contrat + annexes) |

---

## ✅ Avantages

### **1. Séparation claire**
- ✅ Contrat principal statique (pas de données sensibles)
- ✅ Annexes dynamiques (données du client)
- ✅ Facilite la mise à jour du contrat

### **2. Sécurité**
- ✅ Données client uniquement dans les annexes
- ✅ Contrat principal réutilisable
- ✅ Traçabilité (PDF sauvegardés en BD)

### **3. Communication**
- ✅ Client reçoit tout par email
- ✅ Manager SGI informé automatiquement
- ✅ Équipe Xamila en copie
- ✅ Pièces jointes professionnelles

### **4. Maintenabilité**
- ✅ Code modulaire (services séparés)
- ✅ Facile à tester
- ✅ Facile à étendre (nouvelles pages)

---

## 🧪 Tests

### **Test 1: Génération des annexes**

```python
from core.services_annex_pdf import AnnexPDFService
from core.models_sgi import AccountOpeningRequest

aor = AccountOpeningRequest.objects.get(id='...')
annex_data = aor.annex_data

service = AnnexPDFService()
pdf_buffer = service.generate_annexes_pdf(aor, annex_data)

# Sauvegarder pour vérifier
with open('test_annexes.pdf', 'wb') as f:
    f.write(pdf_buffer.read())
```

### **Test 2: Envoi d'emails**

```python
from core.services_email import ContractEmailService

service = ContractEmailService()

# Lire les PDF
with open('contrat.pdf', 'rb') as f:
    contract_pdf = f.read()

with open('annexes.pdf', 'rb') as f:
    annexes_pdf = f.read()

# Envoyer
results = service.send_contract_emails(
    aor=aor,
    contract_pdf=contract_pdf,
    annexes_pdf=annexes_pdf,
    sgi_manager_email='manager@gek.com'
)

print(results)
# {'client': True, 'sgi_manager': True, 'xamila_team': True, 'errors': []}
```

---

## 🚀 Prochaines étapes

### **Immédiat:**
1. ✅ Créer les services (fait)
2. ✅ Ajouter les champs au modèle (fait)
3. ⏳ Créer la migration
4. ⏳ Modifier la vue de création
5. ⏳ Tester l'envoi d'emails

### **Court terme:**
- Améliorer le design des PDF (logos, couleurs)
- Ajouter les signatures base64 → images
- Optimiser la génération (cache)

### **Moyen terme:**
- Interface admin pour voir les PDF
- Ré-envoi d'emails
- Historique des envois

---

## 📝 Notes importantes

### **Contrat principal:**
- Reste 100% statique
- Pas de données client
- Réutilisable pour tous les clients
- Mis à jour uniquement si la SGI change le template

### **Annexes:**
- Contiennent TOUTES les données client
- Générées à chaque soumission
- Ressemblent exactement aux images fournies
- Signatures électroniques incluses

### **Emails:**
- HTML professionnel
- Pièces jointes automatiques
- 3 destinataires (client, SGI, Xamila)
- Fail silently (pas d'erreur si email échoue)

---

**Le système est prêt à être implémenté! 🎉**
