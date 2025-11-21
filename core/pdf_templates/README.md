# 📄 PDF Templates System - Guide complet

## 🎯 Vue d'ensemble

Système modulaire pour gérer les contrats PDF de différentes SGI avec des positions de champs personnalisées.

**Chaque SGI a son propre template** avec:
- Positions (x, y) spécifiques pour chaque champ
- Layout personnalisé
- Gestion des 95 champs des annexes

---

## 📁 Structure

```
core/pdf_templates/
├── __init__.py          # Registry des templates
├── base.py              # Classe de base BasePDFTemplate
├── gek_capital.py       # Template GEK CAPITAL (95 champs)
├── nsia.py              # Template NSIA FINANCE
└── README.md            # Ce fichier
```

---

## 🚀 Comment ajouter une nouvelle SGI

### Étape 1: Créer le fichier template

Créez `core/pdf_templates/ma_sgi.py`:

```python
"""
MA SGI PDF Template with custom field mappings.
"""
import os
from typing import Dict, Any
from django.conf import settings
from reportlab.lib.units import mm
from .base import BasePDFTemplate


class MaSGITemplate(BasePDFTemplate):
    """PDF Template for MA SGI."""
    
    def get_template_path(self) -> str:
        """Return path to MA SGI PDF template."""
        return os.path.join(
            settings.BASE_DIR,
            'contracts',
            'MA_SGI_Convention.pdf'
        )
    
    def fill_page(self, canvas_obj, page_index: int, context: Dict[str, Any]):
        """Fill specific pages with data."""
        annex = self.get_annex_data(context)
        aor = self.get_aor_data(context)
        
        # Page 1: Cover
        if page_index == 0:
            self._fill_cover(canvas_obj, annex, aor)
        
        # Page X: Identity
        elif page_index == 10:  # Adjust to your template
            self._fill_identity(canvas_obj, annex, aor)
    
    def _fill_cover(self, c, annex: Dict, aor):
        """Fill cover page."""
        # Vos positions spécifiques
        x, y = 50 * mm, 250 * mm
        self.draw_text(c, x, y, getattr(aor, 'full_name', ''))
        
        # Email
        p22 = annex.get('page22', {})
        email = self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        self.draw_text(c, x, y - 10 * mm, email)
    
    def _fill_identity(self, c, annex: Dict, aor):
        """Fill identity page with all 55 fields from page22."""
        p22 = annex.get('page22', {})
        
        # Civilité
        civility = self.safe_get(p22, 'civility', 'Monsieur')
        # Ajustez les positions selon votre template
        if civility == 'Monsieur':
            self.draw_checkbox(c, 30 * mm, 260 * mm, True)
        
        # Nom et prénoms
        nom = self.safe_get(p22, 'last_name')
        prenoms = self.safe_get(p22, 'first_names')
        self.draw_text(c, 40 * mm, 250 * mm, nom)
        self.draw_text(c, 40 * mm, 243 * mm, prenoms)
        
        # Date de naissance
        birth_date = self.format_date(self.safe_get(p22, 'birth_date'))
        self.draw_text(c, 40 * mm, 236 * mm, birth_date)
        
        # ... Continuez pour tous les champs
```

### Étape 2: Enregistrer dans le registry

Modifiez `core/pdf_templates/__init__.py`:

```python
from .ma_sgi import MaSGITemplate

TEMPLATE_REGISTRY = {
    'GEK': GEKCapitalTemplate,
    'GEK CAPITAL': GEKCapitalTemplate,
    'NSIA': NSIATemplate,
    'NSIA FINANCE': NSIATemplate,
    'MA SGI': MaSGITemplate,  # ✅ Ajoutez votre SGI
}
```

### Étape 3: Ajouter le fichier PDF template

Placez votre fichier PDF dans:
```
xamila_backend/contracts/MA_SGI_Convention.pdf
```

### Étape 4: Tester

```python
# Le système choisira automatiquement le bon template
# basé sur le nom de la SGI dans la base de données
```

---

## 📋 Liste des 95 champs disponibles

### Page 22 (55 champs)

#### Personne Physique (11 champs):
```python
p22.get('civility')              # Monsieur/Madame/Mademoiselle
p22.get('last_name')             # Nom
p22.get('maiden_name')           # Nom de jeune fille
p22.get('first_names')           # Prénoms
p22.get('birth_date')            # Date de naissance (YYYY-MM-DD)
p22.get('birth_place')           # Lieu de naissance
p22.get('nationality')           # Nationalité
p22.get('id_type')               # Type de pièce
p22.get('id_number')             # Numéro de pièce
p22.get('id_valid_until')        # Date de validité
```

#### Personne Morale (10 champs):
```python
p22.get('is_company')            # Boolean
p22.get('company_name')          # Nom de la société
p22.get('company_ncc')           # Numéro NCC
p22.get('company_rccm')          # Numéro RCCM
p22.get('representative_name')   # Nom du représentant
p22.get('representative_first_names')
p22.get('representative_birth_date')
p22.get('representative_birth_place')
p22.get('representative_nationality')
p22.get('representative_function')
```

#### Adresse Fiscale (8 champs):
```python
p22.get('fiscal_address')        # Résidence, Bâtiment
p22.get('fiscal_street_number')  # N° Rue
p22.get('fiscal_postal_code')    # Code postal
p22.get('fiscal_city')           # Ville
p22.get('fiscal_country')        # Pays
p22.get('is_fiscal_resident_ivory')  # Boolean
p22.get('is_cedeao_member')      # Boolean
p22.get('is_outside_cedeao')     # Boolean
```

#### Adresse Postale (5 champs):
```python
p22.get('postal_address')
p22.get('postal_door_number')
p22.get('postal_code')
p22.get('postal_city')
p22.get('postal_country')
```

#### Coordonnées (4 champs):
```python
p22.get('phone')                 # Tél portable
p22.get('home_phone')            # Tél domicile
p22.get('email')                 # Email
p22.get('email_confirm')         # Confirmation email
```

#### Restrictions (6 champs):
```python
p22.get('is_minor')              # Boolean
p22.get('minor_legal_admin')     # Boolean
p22.get('minor_tutelle')         # Boolean
p22.get('is_protected_adult')    # Boolean
p22.get('protected_curatelle')   # Boolean
p22.get('protected_tutelle')     # Boolean
```

#### Représentant légal (9 champs):
```python
p22.get('guardian_name')
p22.get('guardian_first_names')
p22.get('guardian_birth_date')
p22.get('guardian_birth_place')
p22.get('guardian_nationality')
p22.get('guardian_geo_address')
p22.get('guardian_postal_address')
p22.get('guardian_city')
p22.get('guardian_country')
```

#### Convocation électronique (2 champs):
```python
p22.get('consent_electronic')    # Boolean
p22.get('consent_electronic_docs')  # Boolean
```

### Page 23 (2 champs)

```python
p23 = annex.get('page23', {})
p23.get('consent_email')         # Boolean
p23.get('email')                 # Email alternatif
```

### Page 26 (38 champs)

#### Type de compte (19 champs):
```python
p26 = annex.get('page26', {})
p26.get('account_individual')    # Boolean
p26.get('account_joint')         # Boolean
p26.get('account_indivision')    # Boolean

# Compte joint (7 champs)
p26.get('joint_holder_a_name')
p26.get('joint_holder_a_first_names')
p26.get('joint_holder_a_birth_date')
p26.get('joint_holder_b_name')
p26.get('joint_holder_b_first_names')
p26.get('joint_holder_b_birth_date')

# Compte indivision (9 champs)
p26.get('indivision_holder_a_name')
p26.get('indivision_holder_a_first_names')
p26.get('indivision_holder_b_name')
p26.get('indivision_holder_b_first_names')
p26.get('indivision_holder_c_name')
p26.get('indivision_holder_c_first_names')
p26.get('indivision_holder_d_name')
p26.get('indivision_holder_d_first_names')
```

#### Personne désignée (1 champ):
```python
p26.get('designated_operator_name')
```

#### Signature (2 champs):
```python
p26.get('place')                 # Lieu
p26.get('date')                  # Date (YYYY-MM-DD)
```

#### Procuration (17 champs):
```python
p26.get('has_procuration')       # Boolean

# Mandant (8 champs)
p26.get('mandant_civility')
p26.get('mandant_name')
p26.get('mandant_first_names')
p26.get('mandant_address')
p26.get('mandant_postal_code')
p26.get('mandant_city')
p26.get('mandant_country')
p26.get('account_number')

# Mandataire (7 champs)
p26.get('mandataire_civility')
p26.get('mandataire_name')
p26.get('mandataire_first_names')
p26.get('mandataire_address')
p26.get('mandataire_postal_code')
p26.get('mandataire_city')
p26.get('mandataire_country')

# Signature procuration (2 champs)
p26.get('procuration_place')
p26.get('procuration_date')
```

---

## 🛠️ Méthodes utilitaires de BasePDFTemplate

```python
# Dessiner une checkbox
self.draw_checkbox(canvas_obj, x, y, checked=True)

# Dessiner du texte
self.draw_text(canvas_obj, x, y, "Mon texte")

# Récupérer une valeur en toute sécurité
value = self.safe_get(dict, 'key', default='')

# Formater une date YYYY-MM-DD en DD/MM/YYYY
formatted = self.format_date('2025-01-15')  # → '15/01/2025'

# Récupérer les données
annex = self.get_annex_data(context)
aor = self.get_aor_data(context)
sgi = self.get_sgi_data(context)
```

---

## 📐 Système de coordonnées

ReportLab utilise des millimètres (mm) avec origine en bas à gauche:

```
(0, 297mm) ────────────── (210mm, 297mm)  ← Haut de la page A4
    │                            │
    │                            │
    │                            │
    │                            │
(0, 0) ──────────────────── (210mm, 0)    ← Bas de la page
```

**Exemples de positions:**
- Haut de page: `y = 280 * mm`
- Milieu de page: `y = 148 * mm`
- Bas de page: `y = 20 * mm`
- Gauche: `x = 20 * mm`
- Centre: `x = 105 * mm`
- Droite: `x = 190 * mm`

---

## 🎨 Exemples de code

### Dessiner un titre
```python
c.setFont("Helvetica-Bold", 14)
self.draw_text(c, 105 * mm, 280 * mm, "CONTRAT D'OUVERTURE DE COMPTE")
```

### Dessiner un champ avec label
```python
y = 250 * mm
self.draw_text(c, 30 * mm, y, "Nom:")
self.draw_text(c, 60 * mm, y, self.safe_get(p22, 'last_name'))
```

### Gérer les sections conditionnelles
```python
if self.safe_get(p22, 'is_company', 'false').lower() == 'true':
    # Afficher les champs société
    self.draw_text(c, 30 * mm, 240 * mm, self.safe_get(p22, 'company_name'))
else:
    # Afficher les champs personne physique
    self.draw_text(c, 30 * mm, 240 * mm, self.safe_get(p22, 'last_name'))
```

### Boucler sur des co-titulaires
```python
holders = []
for letter in ['a', 'b', 'c', 'd']:
    name = self.safe_get(p26, f'indivision_holder_{letter}_name')
    if name:
        holders.append(name)

y = 200 * mm
for i, holder in enumerate(holders):
    self.draw_text(c, 30 * mm, y - (i * 7 * mm), f"{i+1}. {holder}")
```

---

## ✅ Checklist pour nouvelle SGI

- [ ] Créer `core/pdf_templates/ma_sgi.py`
- [ ] Hériter de `BasePDFTemplate`
- [ ] Implémenter `get_template_path()`
- [ ] Implémenter `fill_page()` avec tous les index de pages
- [ ] Créer méthodes `_fill_page_X()` pour chaque page
- [ ] Mapper les 95 champs aux positions correctes
- [ ] Ajouter dans `TEMPLATE_REGISTRY` dans `__init__.py`
- [ ] Placer le PDF template dans `contracts/`
- [ ] Tester avec des données réelles
- [ ] Vérifier toutes les pages du PDF généré

---

## 🐛 Debugging

### Voir les données disponibles
```python
def fill_page(self, canvas_obj, page_index: int, context: Dict[str, Any]):
    annex = self.get_annex_data(context)
    print(f"Page {page_index}: {annex}")  # Debug
```

### Dessiner une grille de référence
```python
# Ajouter dans fill_page pour voir les coordonnées
for x in range(0, 210, 10):
    self.draw_text(c, x * mm, 10 * mm, str(x))
for y in range(0, 297, 10):
    self.draw_text(c, 10 * mm, y * mm, str(y))
```

---

## 📚 Ressources

- **ReportLab docs:** https://www.reportlab.com/docs/reportlab-userguide.pdf
- **PyPDF docs:** https://pypdf.readthedocs.io/
- **Liste complète des champs:** `ANNEXES_FIELDS_LIST.md`

---

## 🎯 Résumé

1. **Chaque SGI = 1 classe Python** héritant de `BasePDFTemplate`
2. **Positions personnalisées** pour chaque SGI
3. **95 champs disponibles** depuis les annexes
4. **Système modulaire** facile à étendre
5. **Backward compatible** avec l'ancien système

**Bon développement! 🚀**
