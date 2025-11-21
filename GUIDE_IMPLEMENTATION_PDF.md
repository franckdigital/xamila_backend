# 🚀 Guide d'implémentation - Système PDF séparé

## ✅ Étape 1: Migration de la base de données

```bash
cd xamila_backend
python manage.py makemigrations core
python manage.py migrate core
```

**Vérification:**
```bash
python manage.py shell
>>> from core.models_sgi import AccountOpeningRequest
>>> AccountOpeningRequest._meta.get_field('contract_pdf')
>>> AccountOpeningRequest._meta.get_field('annexes_pdf')
```

---

## ✅ Étape 2: Configuration settings.py

Ajouter dans `xamila/settings.py`:

```python
# Email configuration
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'
XAMILA_TEAM_EMAIL = 'team@xamila.com'  # ⚠️ À configurer

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email backend (développement)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email backend (production - à configurer)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## ✅ Étape 3: Créer les dossiers

```bash
cd xamila_backend
mkdir -p media/contracts/main
mkdir -p media/contracts/annexes
```

**Vérification:**
```bash
ls -la media/contracts/
# Doit afficher: main/ et annexes/
```

---

## ✅ Étape 4: Modifier la vue de création

Éditer `core/views.py` - Fonction `AccountOpeningRequestCreateView.post()`:

**Ajouter après la ligne 635 (après `req_obj = serializer.save()`):**

```python
# Générer les PDF
from core.services_annex_pdf import AnnexPDFService
from core.services_email import ContractEmailService
from django.core.files.base import ContentFile
import os

try:
    # 1. Contrat principal (statique)
    contract_template_path = os.path.join(
        settings.BASE_DIR,
        'contracts',
        'GEK --Convention commerciale VF 2025.pdf'
    )
    
    with open(contract_template_path, 'rb') as f:
        contract_pdf_content = f.read()
    
    # Sauvegarder le contrat
    req_obj.contract_pdf.save(
        f'contrat_{req_obj.id}.pdf',
        ContentFile(contract_pdf_content),
        save=False
    )
    
    # 2. Annexes (dynamiques)
    annex_service = AnnexPDFService()
    annexes_pdf_buffer = annex_service.generate_annexes_pdf(
        req_obj,
        req_obj.annex_data
    )
    
    # Sauvegarder les annexes
    req_obj.annexes_pdf.save(
        f'annexes_{req_obj.id}.pdf',
        ContentFile(annexes_pdf_buffer.read()),
        save=False
    )
    
    req_obj.save()
    
    # 3. Envoyer les emails
    email_service = ContractEmailService()
    sgi_manager_email = None
    if req_obj.sgi:
        sgi_manager_email = getattr(req_obj.sgi, 'manager_email', None)
    
    email_results = email_service.send_contract_emails(
        aor=req_obj,
        contract_pdf=contract_pdf_content,
        annexes_pdf=annexes_pdf_buffer.getvalue(),
        sgi_manager_email=sgi_manager_email
    )
    
    logger.info(f"Emails envoyés: {email_results}")

except Exception as e:
    logger.error(f"Erreur génération/envoi PDF: {e}")
    # Ne pas bloquer la création si les PDF échouent
```

---

## ✅ Étape 5: Tester la génération des PDF

### **Test 1: Générer les annexes**

```python
python manage.py shell

from core.models_sgi import AccountOpeningRequest
from core.services_annex_pdf import AnnexPDFService

# Récupérer une demande
aor = AccountOpeningRequest.objects.first()

# Générer les annexes
service = AnnexPDFService()
pdf_buffer = service.generate_annexes_pdf(aor, aor.annex_data)

# Sauvegarder pour vérifier
with open('/tmp/test_annexes.pdf', 'wb') as f:
    f.write(pdf_buffer.read())

print("PDF généré: /tmp/test_annexes.pdf")
```

### **Test 2: Tester l'envoi d'emails**

```python
from core.services_email import ContractEmailService

service = ContractEmailService()

# Lire les PDF de test
with open('/tmp/contrat.pdf', 'rb') as f:
    contract_pdf = f.read()

with open('/tmp/test_annexes.pdf', 'rb') as f:
    annexes_pdf = f.read()

# Envoyer (en mode console, les emails s'afficheront dans le terminal)
results = service.send_contract_emails(
    aor=aor,
    contract_pdf=contract_pdf,
    annexes_pdf=annexes_pdf,
    sgi_manager_email='test@example.com'
)

print(results)
```

---

## ✅ Étape 6: Tester le flux complet

### **Via l'API:**

```bash
curl -X POST http://localhost:8000/api/account-opening/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sgi_id": "gek-id",
    "full_name": "Test CLIENT",
    "email": "test@example.com",
    "phone": "+225 07 00 00 00 00",
    "country_of_residence": "Côte d'\''Ivoire",
    "nationality": "Ivoirienne",
    "sources_of_income": "Salaire",
    "investor_profile": "PRUDENT",
    "annex_data": {
      "page21": {
        "place": "Abidjan",
        "date": "2025-11-21"
      },
      "page22": {
        "last_name": "CLIENT",
        "first_names": "Test",
        "email": "test@example.com",
        "phone": "+225 07 00 00 00 00"
      }
    }
  }'
```

### **Vérifications:**

1. **Base de données:**
```python
aor = AccountOpeningRequest.objects.latest('created_at')
print(aor.contract_pdf.url)  # /media/contracts/main/contrat_xxx.pdf
print(aor.annexes_pdf.url)   # /media/contracts/annexes/annexes_xxx.pdf
```

2. **Fichiers:**
```bash
ls -lh media/contracts/main/
ls -lh media/contracts/annexes/
```

3. **Emails (console):**
```bash
# Vérifier dans le terminal du serveur Django
# Les emails doivent s'afficher avec:
# - Sujet
# - Destinataires
# - Corps HTML
# - Pièces jointes
```

---

## ✅ Étape 7: Configuration email production

### **Option 1: Gmail**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Pas le mot de passe Gmail!
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

**⚠️ Important:** Utiliser un "App Password" Gmail, pas le mot de passe principal.

### **Option 2: SendGrid**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'YOUR_SENDGRID_API_KEY'
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'
```

### **Option 3: Mailgun**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@your-domain.mailgun.org'
EMAIL_HOST_PASSWORD = 'YOUR_MAILGUN_PASSWORD'
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'
```

---

## ✅ Étape 8: Ajouter au admin Django

Éditer `core/admin.py`:

```python
from django.contrib import admin
from .models_sgi import AccountOpeningRequest

@admin.register(AccountOpeningRequest)
class AccountOpeningRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'sgi', 'status', 'created_at']
    list_filter = ['status', 'sgi', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'contract_pdf', 'annexes_pdf']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('customer', 'full_name', 'email', 'phone')
        }),
        ('SGI', {
            'fields': ('sgi',)
        }),
        ('PDF générés', {
            'fields': ('contract_pdf', 'annexes_pdf'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'status', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression accidentelle
        return request.user.is_superuser
```

---

## 🎯 Checklist finale

- [ ] Migration exécutée
- [ ] Settings.py configuré
- [ ] Dossiers media créés
- [ ] Vue modifiée
- [ ] Test génération PDF OK
- [ ] Test envoi email OK
- [ ] Admin Django configuré
- [ ] Email production configuré
- [ ] Test flux complet OK

---

## 🐛 Dépannage

### **Problème: PDF non généré**

```python
# Vérifier les logs
tail -f xamila_backend/django_debug.log

# Vérifier les permissions
ls -la media/contracts/
chmod 755 media/contracts/main
chmod 755 media/contracts/annexes
```

### **Problème: Email non envoyé**

```python
# Vérifier la configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])

# Vérifier les logs
tail -f xamila_backend/django_debug.log | grep -i email
```

### **Problème: Fichiers trop gros**

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

---

## 📚 Ressources

- **ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Django Email:** https://docs.djangoproject.com/en/4.2/topics/email/
- **PyPDF:** https://pypdf.readthedocs.io/

---

**Bonne implémentation! 🚀**
