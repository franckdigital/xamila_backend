# ✅ Correction - Erreur génération PDF

## ❌ Erreur rencontrée

```
❌ Erreur: Erreur génération PDF: AccountOpeningRequest() got unexpected keyword arguments: 'prefers_service_quality_over_fees'
```

---

## 🔍 Diagnostic

### **Cause:**
Typo dans le nom du champ - différence entre le modèle et la vue.

**Modèle (`models_sgi.py` ligne 503):**
```python
prefer_service_quality_over_fees = models.BooleanField(default=True)
```

**Vue (`views.py` ligne 330) - AVANT:**
```python
prefers_service_quality_over_fees=bool(data.get('prefer_service_quality_over_fees'))
#       ↑ 's' en trop ici
```

### **Erreur:**
Le nom du paramètre dans la création de l'objet `AccountOpeningRequest` ne correspond pas au nom du champ du modèle.

---

## ✅ Correction appliquée

**Fichier:** `core/views.py` ligne 330

**Avant:**
```python
prefers_service_quality_over_fees=bool(data.get('prefer_service_quality_over_fees')),
```

**Après:**
```python
prefer_service_quality_over_fees=bool(data.get('prefer_service_quality_over_fees')),
```

**Changement:** Suppression du 's' en trop dans `prefers` → `prefer`

---

## 🎯 Contexte

Cette erreur se produisait dans la vue `ContractPDFPreviewView` lors de la création d'un objet `AccountOpeningRequest` temporaire (non sauvegardé) pour générer le PDF de prévisualisation.

**Code complet (lignes 312-335):**
```python
# Build a transient AOR object (not saved)
aor = AccountOpeningRequest(
    customer=request.user,
    sgi=sgi,
    full_name=data.get('full_name') or request.user.get_full_name() or '',
    email=data.get('email') or request.user.email or '',
    phone=data.get('phone') or getattr(request.user, 'phone', '') or '',
    country_of_residence=data.get('country_of_residence') or getattr(request.user, 'country_of_residence', '') or '',
    nationality=data.get('nationality') or getattr(request.user, 'country', '') or '',
    customer_banks_current_account=[],
    wants_digital_opening=str(data.get('wants_digital_opening', 'true')).lower() == 'true',
    wants_in_person_opening=str(data.get('wants_in_person_opening', 'false')).lower() == 'true',
    available_minimum_amount=data.get('available_minimum_amount') or None,
    wants_100_percent_digital_sgi=str(data.get('wants_100_percent_digital_sgi', 'false')).lower() == 'true',
    funding_by_visa=str(data.get('funding_by_visa', 'false')).lower() == 'true',
    funding_by_mobile_money=str(data.get('funding_by_mobile_money', 'false')).lower() == 'true',
    funding_by_bank_transfer=str(data.get('funding_by_bank_transfer', 'false')).lower() == 'true',
    funding_by_intermediary=str(data.get('funding_by_intermediary', 'false')).lower() == 'true',
    funding_by_wu_mg_ria=str(data.get('funding_by_wu_mg_ria', 'false')).lower() == 'true',
    prefer_service_quality_over_fees=bool(data.get('prefer_service_quality_over_fees')),  # ✅ CORRIGÉ
    sources_of_income=data.get('sources_of_income') or '',
    investor_profile=data.get('investor_profile') or 'PRUDENT',
    holder_info=data.get('holder_info') or '',
    annex_data=annex_data,
)
```

---

## 🧪 Test

### **Avant la correction:**
```bash
POST /api/account-opening/contract/preview/
→ 500 Internal Server Error
→ AccountOpeningRequest() got unexpected keyword arguments: 'prefers_service_quality_over_fees'
```

### **Après la correction:**
```bash
POST /api/account-opening/contract/preview/
→ 200 OK
→ PDF généré avec succès
```

---

## 📝 Vérifications supplémentaires

### **1. Vérifier les autres occurrences:**

```bash
cd xamila_backend
grep -r "prefers_service_quality_over_fees" .
```

**Résultat:** Aucune autre occurrence (après correction)

### **2. Vérifier la cohérence des noms de champs:**

| Champ | Modèle | Serializer | Vue | Frontend |
|-------|--------|------------|-----|----------|
| prefer_service_quality_over_fees | ✅ | ✅ | ✅ | ✅ |

---

## ✅ Résultat

**La génération de PDF fonctionne maintenant correctement! 🎉**

### **Test de prévisualisation:**

1. Remplir le formulaire d'ouverture de compte
2. Cliquer sur "Télécharger le contrat"
3. Le PDF se génère et se télécharge automatiquement

### **Message de succès:**

```
✅ Contrat téléchargé: Contrat_GEK_CAPITAL_Jean_KOUASSI_2025-11-21.pdf
```

---

## 🔧 Recommandations

### **Pour éviter ce type d'erreur à l'avenir:**

1. **Utiliser des constantes pour les noms de champs:**
```python
# Dans models_sgi.py
class AccountOpeningRequest(models.Model):
    FIELD_PREFER_QUALITY = 'prefer_service_quality_over_fees'
    prefer_service_quality_over_fees = models.BooleanField(default=True)
```

2. **Utiliser le serializer pour créer les objets:**
```python
# Au lieu de créer manuellement
serializer = AccountOpeningRequestSerializer(data=data)
if serializer.is_valid():
    aor = serializer.save()
```

3. **Tests unitaires:**
```python
def test_pdf_preview_creation():
    """Test que la création d'AOR pour preview fonctionne"""
    data = {...}
    aor = AccountOpeningRequest(**data)
    assert aor.prefer_service_quality_over_fees is not None
```

---

## 📌 Résumé

| Aspect | Détail |
|--------|--------|
| **Erreur** | Typo dans le nom du champ |
| **Fichier** | `core/views.py` ligne 330 |
| **Correction** | `prefers_` → `prefer_` |
| **Impact** | Génération PDF preview |
| **Status** | ✅ Corrigé |

**La prévisualisation PDF fonctionne maintenant! 🎉**
