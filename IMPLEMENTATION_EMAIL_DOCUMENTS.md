# Implémentation de l'envoi d'emails avec tous les documents

## ✅ Ce qui a été fait

### 1. Service d'email amélioré (`core/services_email.py`)

Le service `ContractEmailService` a été modifié pour :

- ✅ Envoyer le **contrat complet** (PDF)
- ✅ Envoyer les **annexes pré-remplies** (PDF)
- ✅ Envoyer la **photo d'identité** (JPG/PNG)
- ✅ Envoyer la **pièce d'identité** (PDF/JPG/PNG)
- ✅ Support pour les **emails admin** en plus du client, SGI manager et équipe Xamila

### 2. Destinataires des emails

Les documents sont envoyés à :
1. **Client** - Email de confirmation avec tous les documents
2. **Manager SGI** - Notification avec tous les documents
3. **Équipe Xamila** - Notification interne avec tous les documents
4. **Administrateurs** - Email admin avec tous les documents (nouveau)

### 3. Méthode `send_contract_emails`

```python
def send_contract_emails(
    self,
    aor,  # AccountOpeningRequest instance
    contract_pdf: bytes,  # Contrat complet
    annexes_pdf: bytes,  # Annexes pré-remplies
    sgi_manager_email: Optional[str] = None,
    admin_emails: Optional[List[str]] = None
) -> dict:
```

**Retour:**
```python
{
    'client': True/False,
    'sgi_manager': True/False,
    'xamila_team': True/False,
    'admin': True/False,
    'errors': [...]
}
```

---

## 📋 Ce qu'il reste à faire

### Étape 1 : Modifier la vue de soumission

La vue `AccountOpeningRequestCreateView` (ligne 653 de `views.py`) doit être modifiée pour :

1. **Générer le contrat complet** avec le service `ContractPDFService`
2. **Générer les annexes** avec le service `AnnexPDFService`
3. **Sauvegarder les PDFs** dans le modèle `AccountOpeningRequest`
4. **Utiliser le nouveau service d'email** `ContractEmailService`
5. **Récupérer les emails admin** depuis la base de données

### Exemple de code à ajouter :

```python
from .services_email import ContractEmailService
from .services_pdf import ContractPDFService
from .services_annex_pdf import AnnexPDFService
from .models import User
from django.core.files.base import ContentFile

# Après la création de req_obj (ligne 666)
try:
    # 1. Générer le contrat complet
    pdf_service = ContractPDFService()
    ctx = pdf_service.build_context(req_obj)
    html = pdf_service.render_html(ctx)
    contract_response = pdf_service.generate_pdf_response(html)
    contract_pdf_bytes = contract_response.content
    
    # 2. Générer les annexes pré-remplies
    annex_service = AnnexPDFService()
    annex_data = req_obj.annex_data or {}
    annexes_buffer = annex_service.generate_annex_pdf(req_obj, annex_data)
    annexes_pdf_bytes = annexes_buffer.read()
    annexes_buffer.seek(0)
    
    # 3. Sauvegarder les PDFs dans le modèle
    req_obj.contract_pdf.save(
        f'contrat_{req_obj.id}.pdf',
        ContentFile(contract_pdf_bytes),
        save=False
    )
    req_obj.annexes_pdf.save(
        f'annexes_{req_obj.id}.pdf',
        ContentFile(annexes_pdf_bytes),
        save=False
    )
    req_obj.save()
    
    # 4. Récupérer les emails admin
    admin_emails = list(
        User.objects.filter(role='ADMIN', is_active=True)
        .values_list('email', flat=True)
    )
    
    # 5. Récupérer l'email du manager SGI
    sgi_manager_email = None
    if req_obj.sgi:
        sgi_manager_email = getattr(req_obj.sgi, 'manager_email', None)
    
    # 6. Envoyer les emails avec tous les documents
    email_service = ContractEmailService()
    email_results = email_service.send_contract_emails(
        aor=req_obj,
        contract_pdf=contract_pdf_bytes,
        annexes_pdf=annexes_pdf_bytes,
        sgi_manager_email=sgi_manager_email,
        admin_emails=admin_emails
    )
    
    logger.info(f"Emails envoyés: {email_results}")
    
except Exception as e:
    logger.error(f"Erreur génération/envoi documents: {e}")
    # Continuer même en cas d'erreur
```

### Étape 2 : Configuration des emails

Dans `settings.py`, ajouter :

```python
# Email settings
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'
XAMILA_TEAM_EMAIL = 'team@xamila.com'
```

### Étape 3 : Tests

1. **Test unitaire** du service d'email
2. **Test d'intégration** de la vue de soumission
3. **Test manuel** avec un vrai formulaire

---

## 🎯 Flux complet

```
1. Client remplit le formulaire
   ↓
2. Frontend envoie POST /api/account-opening/request/
   ↓
3. Backend crée AccountOpeningRequest
   ↓
4. Backend génère contrat PDF + annexes PDF
   ↓
5. Backend sauvegarde les PDFs en base de données
   ↓
6. Backend envoie 4 emails avec pièces jointes:
   - Client (contrat + annexes + photo + CNI)
   - Manager SGI (contrat + annexes + photo + CNI)
   - Équipe Xamila (contrat + annexes + photo + CNI)
   - Admins (contrat + annexes + photo + CNI)
   ↓
7. Backend retourne succès au frontend
   ↓
8. Frontend affiche modal de succès
```

---

## 📁 Fichiers modifiés

- ✅ `core/services_email.py` - Service d'email avec photo et CNI
- ✅ `core/services_annex_pdf.py` - Label SGI dynamique
- ⏳ `core/views.py` - À modifier pour utiliser le nouveau service
- ✅ `core/models_sgi.py` - Modèle déjà prêt avec champs photo et id_card_scan

---

## 🔧 Configuration serveur

### Variables d'environnement

```bash
# Dans .env ou settings.py
DEFAULT_FROM_EMAIL=noreply@xamila.com
XAMILA_TEAM_EMAIL=team@xamila.com

# Configuration SMTP (si pas déjà fait)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Permissions fichiers

```bash
# S'assurer que Django peut écrire dans les dossiers media
chmod 755 /var/www/xamila/xamila_backend/media
chmod 755 /var/www/xamila/xamila_backend/media/kyc
chmod 755 /var/www/xamila/xamila_backend/media/contracts
```

---

## 📊 Stockage en base de données

Le modèle `AccountOpeningRequest` stocke :

```python
class AccountOpeningRequest(models.Model):
    # ... autres champs ...
    
    # Documents KYC
    photo = models.ImageField(upload_to="kyc/account_opening/photos/")
    id_card_scan = models.FileField(upload_to="kyc/account_opening/id_scans/")
    
    # PDFs générés
    contract_pdf = models.FileField(upload_to="contracts/main/")
    annexes_pdf = models.FileField(upload_to="contracts/annexes/")
    
    # Données annexes
    annex_data = models.JSONField(default=dict)
```

Tous les documents sont sauvegardés et peuvent être récupérés ultérieurement.

---

## ✅ Checklist finale

- [x] Service d'email modifié pour inclure photo et CNI
- [x] Méthode `_send_admin_email` ajoutée
- [x] Label SGI dynamique dans les annexes
- [ ] Vue de soumission modifiée pour utiliser le nouveau service
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Déploiement en production
- [ ] Configuration SMTP vérifiée
- [ ] Test end-to-end avec vrai formulaire

---

## 🚀 Déploiement

```bash
# Backend
ssh root@72.60.88.93
cd /var/www/xamila/xamila_backend
git pull origin master
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
sudo systemctl restart xamila

# Vérifier les logs
sudo journalctl -u xamila -f
```

---

## 📝 Notes importantes

1. **Taille des emails** : Les emails peuvent être volumineux avec tous les documents. Vérifier les limites SMTP.
2. **Performance** : La génération des PDFs peut prendre du temps. Envisager une tâche asynchrone (Celery).
3. **Sécurité** : Les documents contiennent des données sensibles. S'assurer que les emails sont chiffrés (TLS).
4. **Logs** : Tous les envois sont loggés pour traçabilité.
5. **Erreurs** : Le système continue même si un email échoue. Les erreurs sont dans `results['errors']`.
