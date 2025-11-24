# 🗑️ Suppression des pages d'annexes des contrats vierges

## 🎯 Objectif

Supprimer les pages **21, 22, 23 et 26** des contrats vierges commerciaux car ces pages seront remplacées par les **annexes pré-remplies** générées par ReportLab.

---

## 📋 Pages à supprimer

| Page | Contenu | Raison |
|------|---------|--------|
| **21** | Texte légal + Signatures vierges | Remplacée par annexe avec signatures réelles |
| **22** | Formulaire d'ouverture vierge | Remplacée par formulaire pré-rempli |
| **23** | Caractéristiques compte vierges | Remplacée par caractéristiques pré-remplies |
| **26** | Procuration vierge | Remplacée par procuration pré-remplie |

---

## 🔧 Méthode 1 : Script Python (Serveur)

### **Sur le serveur de production**

```bash
cd /var/www/xamila/xamila_backend

# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter le script
python remove_annex_pages.py
```

Le script va :
1. ✅ Créer une sauvegarde de chaque fichier (`.backup`)
2. ✅ Supprimer les pages 21, 22, 23, 26
3. ✅ Sauvegarder les fichiers modifiés

### **Vérification**

```bash
# Vérifier le nombre de pages avant/après
pdfinfo contracts/NSIA_Convention_Compte_Titres.pdf | grep Pages
pdfinfo contracts/NSIA_Convention_Compte_Titres.pdf.backup | grep Pages

# Différence attendue : -4 pages
```

---

## 🔧 Méthode 2 : Outil en ligne (Manuel)

Si vous préférez une approche manuelle :

### **Outils recommandés**

1. **PDFtk** (ligne de commande)
   ```bash
   # Installer PDFtk
   sudo apt-get install pdftk
   
   # Supprimer les pages 21, 22, 23, 26
   pdftk input.pdf cat 1-20 24-25 27-end output output.pdf
   ```

2. **iLovePDF** (en ligne)
   - Aller sur https://www.ilovepdf.com/delete-pdf-pages
   - Uploader le PDF
   - Sélectionner les pages 21, 22, 23, 26
   - Supprimer et télécharger

3. **Adobe Acrobat** (logiciel)
   - Ouvrir le PDF
   - Aller dans "Organiser les pages"
   - Sélectionner les pages 21, 22, 23, 26
   - Clic droit → Supprimer
   - Enregistrer

---

## 📊 Structure avant/après

### **Avant (exemple NSIA)**
```
Pages 1-20  : Conditions générales
Page 21     : Texte légal + Signatures VIERGES ❌
Page 22     : Formulaire d'ouverture VIERGE ❌
Page 23     : Caractéristiques compte VIERGES ❌
Pages 24-25 : Autres clauses
Page 26     : Procuration VIERGE ❌
Pages 27+   : Annexes supplémentaires
```

### **Après**
```
Pages 1-20  : Conditions générales
Pages 21-22 : Autres clauses (anciennes pages 24-25)
Pages 23+   : Annexes supplémentaires (anciennes pages 27+)
```

### **À l'envoi par email**
```
📎 Contrat vierge (pages 1-20 + autres clauses)
📎 Annexes pré-remplies (pages 21, 22, 23, 26 avec données)
```

---

## 🔄 Workflow complet

### **1. Préparation des contrats vierges**
```bash
# Supprimer les pages d'annexes vierges
python remove_annex_pages.py
```

### **2. Soumission d'une demande**
```python
# Backend charge le contrat vierge (sans pages 21-26)
contract_pdf_bytes = load_blank_contract(sgi_name)

# Backend génère les annexes pré-remplies (pages 21-26)
annexes_pdf_bytes = generate_annexes(aor, annex_data)
```

### **3. Envoi des emails**
```
Email au client :
├── Contrat_NSIA_[Nom].pdf      (pages 1-20 + autres)
├── Annexes_NSIA_[Nom].pdf      (pages 21, 22, 23, 26 pré-remplies)
├── Photo_[Nom].jpg
└── CNI_[Nom].pdf
```

---

## ✅ Avantages

### **Avant (avec pages vierges)**
- ❌ Duplication : Pages vierges + Pages pré-remplies
- ❌ Confusion : Quelle version utiliser ?
- ❌ Taille : PDFs plus lourds

### **Après (sans pages vierges)**
- ✅ Pas de duplication
- ✅ Clarté : Contrat vierge + Annexes pré-remplies séparés
- ✅ Taille optimisée
- ✅ Le client sait exactement quoi utiliser

---

## 🧪 Tests à effectuer

### **Test 1 : Vérifier le nombre de pages**
```bash
# NSIA avant : ~30 pages
# NSIA après : ~26 pages (-4 pages)

# GEK avant : ~25 pages
# GEK après : ~21 pages (-4 pages)
```

### **Test 2 : Vérifier le contenu**
1. Ouvrir le contrat vierge modifié
2. ✅ Vérifier que les pages 21-26 originales sont absentes
3. ✅ Vérifier que les autres pages sont intactes
4. ✅ Vérifier que la numérotation est correcte

### **Test 3 : Tester l'envoi d'email**
1. Soumettre une demande
2. ✅ Vérifier que le contrat vierge ne contient PAS les pages 21-26
3. ✅ Vérifier que les annexes pré-remplies contiennent les pages 21, 22, 23, 26
4. ✅ Vérifier qu'il n'y a pas de duplication

---

## 🚨 Sauvegarde et restauration

### **Sauvegardes automatiques**
Le script crée automatiquement des sauvegardes :
```
contracts/
├── NSIA_Convention_Compte_Titres.pdf         (modifié)
├── NSIA_Convention_Compte_Titres.pdf.backup  (original)
├── GEK --Convention commerciale VF 2025.pdf  (modifié)
└── GEK --Convention commerciale VF 2025.pdf.backup  (original)
```

### **Restaurer en cas de problème**
```bash
cd /var/www/xamila/xamila_backend/contracts

# Restaurer NSIA
cp "NSIA_Convention_Compte_Titres.pdf.backup" "NSIA_Convention_Compte_Titres.pdf"

# Restaurer GEK
cp "GEK --Convention commerciale VF 2025.pdf.backup" "GEK --Convention commerciale VF 2025.pdf"
```

---

## 📝 Fichiers concernés

### **Backend**
- `contracts/NSIA_Convention_Compte_Titres.pdf` (à modifier)
- `contracts/GEK --Convention commerciale VF 2025.pdf` (à modifier)
- `remove_annex_pages.py` (script de suppression)

### **Aucun changement de code nécessaire**
Le code backend charge déjà les contrats vierges tels quels. Une fois les pages supprimées, tout fonctionnera automatiquement.

---

## 🎯 Résultat final

**Le client reçoit :**

1. **Contrat vierge** (sans pages 21-26)
   - Pages 1-20 : Conditions générales
   - Autres clauses et annexes générales

2. **Annexes pré-remplies** (pages 21, 22, 23, 26)
   - Page 21 : Texte légal + Signatures réelles
   - Page 22 : Formulaire avec données du client
   - Page 23 : Caractéristiques avec données
   - Page 26 : Procuration avec données

3. **Photo + CNI**

**Avantages :**
- ✅ Pas de confusion
- ✅ Pas de duplication
- ✅ Documents clairs et séparés
- ✅ Le client sait exactement quoi faire

---

## 🚀 Déploiement

### **Étapes**
```bash
# 1. Se connecter au serveur
ssh user@server

# 2. Aller dans le répertoire
cd /var/www/xamila/xamila_backend

# 3. Activer l'environnement virtuel
source venv/bin/activate

# 4. Exécuter le script
python remove_annex_pages.py

# 5. Vérifier les résultats
ls -lh contracts/*.pdf
ls -lh contracts/*.backup

# 6. Tester avec une demande
# Soumettre une demande et vérifier les emails
```

---

**Les pages d'annexes vierges seront supprimées des contrats commerciaux ! 🎉**

Le client recevra :
- **Contrat vierge** (sans pages 21-26 vierges)
- **Annexes pré-remplies** (pages 21-26 avec ses données)

Plus de duplication, plus de confusion !
